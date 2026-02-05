"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import time
import urllib.error
from types import SimpleNamespace

import pytest
from rest_framework.authtoken.models import Token
from elasticmock import _get_elasticmock, ELASTIC_INSTANCES
from unittest.mock import patch
from contextlib import ExitStack

import trackhubs
from thr.settings import BASE_DIR
import elasticsearch
from trackhubs.models import Trackdb
import elasticmock.fake_elasticsearch


def _create_hub(*, user, data_type, url, name="JASPAR_TFBS", short_label="JASPAR TFBS",
                long_label="TFBS predictions for profiles in the JASPAR CORE collections",
                description_url="http://jaspar.genereg.net/genome-tracks/", email="wyeth@cmmt.ubc.ca"):
    """
    Helper to create a Hub with consistent defaults.
    We centralize this to avoid repeating the same object setup across fixtures.
    """
    return trackhubs.models.Hub.objects.create(
        name=name,
        shortLabel=short_label,
        longLabel=long_label,
        url=url,
        description_url=description_url,
        email=email,
        data_type=data_type,
        owner=user
    )


def _create_assembly(*, accession, name, long_name="", ucsc_synonym=""):
    """
    Helper to create an Assembly with explicit defaults.
    """
    return trackhubs.models.Assembly.objects.create(
        accession=accession,
        name=name,
        long_name=long_name,
        ucsc_synonym=ucsc_synonym
    )


def _create_trackdb(*, hub, assembly, species, source_url):
    """
    Helper to create a Trackdb with consistent timestamps.
    """
    return trackhubs.models.Trackdb.objects.create(
        public=True,
        created=int(time.time()),
        updated=int(time.time()),
        assembly=assembly,
        hub=hub,
        species=species,
        source_url=source_url
    )


def _create_track(*, trackdb, file_type, visibility, name, short_label, long_label, big_data_url, parent=None):
    """
    Helper to create a Track with consistent defaults.
    """
    return trackhubs.models.Track.objects.create(
        name=name,
        shortLabel=short_label,
        longLabel=long_label,
        big_data_url=big_data_url,
        parent=parent,
        trackdb=trackdb,
        file_type=file_type,
        visibility=visibility
    )


@pytest.fixture(autouse=True)
def elasticsearch_mock():
    """
    Route all Elasticsearch clients to ElasticMock during tests.
    This avoids requiring a real ES service for unit tests.
    """
    ELASTIC_INSTANCES.clear()
    with ExitStack() as stack:
        stack.enter_context(patch("elasticsearch.Elasticsearch", _get_elasticmock))
        stack.enter_context(patch("elasticsearch.client.Elasticsearch", _get_elasticmock))
        try:
            stack.enter_context(patch("elasticsearch_dsl.connections.Elasticsearch", _get_elasticmock))
        except Exception:
            # elasticsearch_dsl may not be importable outside the test environment
            pass
        yield


@pytest.fixture(scope="session")
def django_db_use_migrations():
    """
    Disable migrations in tests to allow syncdb-style table creation.
    We do this because this repo doesn't ship migrations.
    """
    return False


@pytest.fixture(autouse=True)
def hubcheck_requests_mock(monkeypatch):
    """
    Mock requests to the hubCheck service.
    """
    class _Resp:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload
            self.ok = 200 <= status_code < 300
            self.text = ""

        def json(self):
            return self._payload

    def _fake_get(url, params=None, **kwargs):
        hub_url = (params or {}).get("hub_url", "")
        if "Rfam/12.0/genome_browser_hub/hub.txt" in hub_url:
            return _Resp(200, {"success": {"mock": True}})
        if "Track_Hubs/SRP090583/hub.txt" in hub_url:
            return _Resp(200, {"warning": {"mock": True}})
        if "databases/not/here/hub.txt" in hub_url:
            return _Resp(200, {"error": {"mock": True}})
        return _Resp(200, {"error": {"mock": True}})

    # Patch the module reference in hub_check without mutating the global requests module.
    # We keep requests.get intact so libraries like responses continue to work.
    monkeypatch.setattr("trackhubs.hub_check.requests", SimpleNamespace(get=_fake_get))


@pytest.fixture(autouse=True)
def urlopen_mock(monkeypatch):
    """
    Mock urllib.request.urlopen for deterministic tests in trackhubs.tracks_status.
    """
    class _Resp:
        def __init__(self, code=200, body=b""):
            self._code = code
            self._body = body

        def getcode(self):
            return self._code

        def read(self):
            return self._body

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    hub_txt = "\n".join([
        "hub JASPAR_TFBS",
        "shortLabel JASPAR TFBS",
        "longLabel TFBS predictions for profiles in the JASPAR CORE collections",
        "genomesFile genomes.txt",
        "email wyeth@cmmt.ubc.ca",
        "descriptionUrl http://jaspar.genereg.net/genome-tracks/",
        "",
    ]).encode("utf-8")

    genomes_txt = "\n".join([
        "genome hg19",
        "trackDb hg19/trackDb.txt",
        "",
        "genome hg38",
        "trackDb hg38/trackDb.txt",
        "",
    ]).encode("utf-8")

    trackdb_hg19 = "\n".join([
        "track JASPAR2020_TFBS_hg19",
        "shortLabel JASPAR2020 TFBS hg19",
        "longLabel TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2020)",
        "html http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/JASPAR2020_TFBS_help.html",
        "type bigBed 6 +",
        "maxItems 100000",
        "labelFields name",
        "defaultLabelFields name",
        "searchIndex name",
        "visibility pack",
        "spectrum on",
        "scoreFilter 400",
        "scoreFilterRange 0:1000",
        "bigDataUrl http://expdata.cmmt.ubc.ca/JASPAR/downloads/UCSC_tracks/2020/JASPAR2020_hg19.bb",
        "nameFilterText *",
        "",
    ]).encode("utf-8")

    trackdb_hg38 = "\n".join([
        "track JASPAR2020_TFBS_hg38",
        "shortLabel JASPAR2020 TFBS hg38",
        "longLabel TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2020)",
        "html http://expdata.cmmt.ubc.ca/JASPAR/UCSC_tracks/JASPAR2020_TFBS_help.html",
        "type bigBed 6 +",
        "visibility pack",
        "bigDataUrl http://expdata.cmmt.ubc.ca/JASPAR/downloads/UCSC_tracks/2020/JASPAR2020_hg38.bb",
        "",
    ]).encode("utf-8")

    def _fake_urlopen(url, *args, **kwargs):
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        if url == "":
            raise urllib.error.URLError("Empty URL")

        if url == "https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt":
            return _Resp(200, hub_txt)
        if url == "https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/genomes.txt":
            return _Resp(200, genomes_txt)
        if url == "https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hg19/trackDb.txt":
            return _Resp(200, trackdb_hg19)
        if url == "https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hg38/trackDb.txt":
            return _Resp(200, trackdb_hg38)

        if url == "https://data.broadinstitute.org/compbio1/PhyloCSFtracks/trackHub/hub.ttxt":
            raise urllib.error.URLError("Not Found")
        if url == "https://invalide.url/hub.txt":
            raise urllib.error.URLError("Name or service not known")

        if url == "http://expdata.cmmt.ubc.ca/JASPAR/downloads/UCSC_tracks/2020/JASPAR2020_hg38.bb":
            return _Resp(200)
        if url == "ftp://ftp.sra.ebi.ac.uk/vol1/ERZ113/ERZ1131357/SRR2922672.cram":
            return _Resp(None)
        if url == "ftp://ftp.sra.ebi.ac.uk/bar.cram":
            raise urllib.error.URLError(
                "ftp error: URLError(\"ftp error: error_perm('550 Failed to change directory.')\")"
            )
        if url == "http://some.org/random/url/foo.cram":
            raise urllib.error.HTTPError(url, 403, "Forbidden", hdrs=None, fp=None)

        return _Resp(200)

    # We route both track status checks and parser downloads through the same stubbed urlopen.
    monkeypatch.setattr("trackhubs.tracks_status.urllib.request.urlopen", _fake_urlopen)
    monkeypatch.setattr("trackhubs.parser.urllib.request.urlopen", _fake_urlopen)


@pytest.fixture(autouse=True)
def search_trackdb_document_mock(monkeypatch):
    """
    Mock TrackdbDocument.get to fetch from the DB instead of Elasticsearch.
    """
    def _fake_get(cls, id=None, **kwargs):
        try:
            trackdb = Trackdb.objects.filter(trackdb_id=id).select_related(
                "hub", "species", "assembly"
            ).first()
        except RuntimeError:
            # DB access not allowed in this test; behave like ES not found.
            raise elasticsearch.exceptions.NotFoundError(404, "not_found", {})
        if not trackdb:
            raise elasticsearch.exceptions.NotFoundError(404, "not_found", {})

        data = {
            "trackdb_id": trackdb.trackdb_id,
            "version": trackdb.version,
            "created": trackdb.created,
            "status": trackdb.status,
            "owner": trackdb.hub.get_owner(),
            "type": trackdb.hub.data_type.name if trackdb.hub.data_type else "",
            "source": {"url": trackdb.source_url},
            "hub": {
                "name": trackdb.hub.name,
                "shortLabel": trackdb.hub.shortLabel,
                "longLabel": trackdb.hub.longLabel,
                "url": trackdb.hub.url,
                "description_url": trackdb.hub.description_url,
                "email": trackdb.hub.email,
            },
            "species": {
                "taxon_id": trackdb.species.taxon_id,
                "scientific_name": trackdb.species.scientific_name,
                "common_name": trackdb.species.common_name,
            },
            "assembly": {
                "accession": trackdb.assembly.accession,
                "name": trackdb.assembly.name,
                "long_name": trackdb.assembly.long_name,
                "ucsc_synonym": trackdb.assembly.ucsc_synonym,
            },
        }
        # SimpleNamespace keeps attribute access without introducing non-serializable wrappers.
        return SimpleNamespace(**data)

    monkeypatch.setattr("search.documents.TrackdbDocument.get", classmethod(_fake_get))


@pytest.fixture(autouse=True)
def disable_trackdb_es_updates(monkeypatch):
    """
    Disable Trackdb.update_trackdb_document ES updates during tests.
    """
    def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr("trackhubs.models.Trackdb.update_trackdb_document", _noop)


@pytest.fixture(autouse=True)
def elasticmock_behavior_patch(monkeypatch):
    """
    Provide minimal FakeElasticsearch behavior for index/get/update in tests.
    """
    def _ensure_store(self):
        if not hasattr(self, "_store"):
            self._store = {}

    def _index(self, index=None, id=None, body=None, **kwargs):
        _ensure_store(self)
        idx = self._store.setdefault(index, {})
        result = "updated" if id in idx else "created"
        idx[id] = body
        return {"result": result}

    def _get(self, index=None, id=None, **kwargs):
        _ensure_store(self)
        try:
            return {"_source": self._store[index][id]}
        except Exception:
            raise elasticsearch.exceptions.NotFoundError(404, "not_found", {})

    def _update(self, index=None, id=None, body=None, **kwargs):
        _ensure_store(self)
        idx = self._store.setdefault(index, {})
        doc = idx.get(id, {})
        if body and "doc" in body:
            doc.update(body["doc"])
        idx[id] = doc
        return {"result": "updated"}

    monkeypatch.setattr(elasticmock.fake_elasticsearch.FakeElasticsearch, "index", _index, raising=False)
    monkeypatch.setattr(elasticmock.fake_elasticsearch.FakeElasticsearch, "get", _get, raising=False)
    monkeypatch.setattr(elasticmock.fake_elasticsearch.FakeElasticsearch, "update", _update, raising=False)


@pytest.fixture
def project_dir():
    """
    INFO: this fixture isn't used for now because it breaks CI tests
    """
    return BASE_DIR.parent


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture()
def create_user_resource(django_user_model):
    """
    Create a temporary user then return the user and token
    """
    user = django_user_model.objects.create_user(username='testuser', password='test-password', email='testuser@mail.com')
    token, _ = Token.objects.get_or_create(user=user)
    return user, token


@pytest.fixture()
def create_datatype_resource():
    """
    Create a temporary DataType object
    The created DataType will be used in various tests below
    """
    return trackhubs.models.DataType.objects.create(name='genomics')


@pytest.fixture()
def create_filetype_resource():
    return trackhubs.models.FileType.objects.create(name='bam')


@pytest.fixture()
def create_visibility_resource():
    return trackhubs.models.Visibility.objects.create(name='pack')


@pytest.fixture()
def create_species_resource():
    return trackhubs.models.Species.objects.create(taxon_id=9606, scientific_name='Homo sapiens')


@pytest.fixture()
def create_genome_assembly_dump_resource():
    hg19_dump = trackhubs.models.GenomeAssemblyDump(
        accession='GCA_000001405',
        version=1,
        accession_with_version='GCA_000001405.1',
        assembly_name='GRCh37',
        assembly_title='Genome Reference Consortium Human Build 37 (GRCh37)',
        tax_id=9606,
        scientific_name='Homo sapiens',
        ucsc_synonym='hg19',
        api_last_updated='2013-08-08'
    )
    hg38_dump = trackhubs.models.GenomeAssemblyDump(
        accession='GCA_000001405',
        version=15,
        accession_with_version='GCA_000001405.15',
        assembly_name='GRCh38',
        assembly_title='Genome Reference Consortium Human Build 38',
        tax_id=9606,
        scientific_name='Homo sapiens',
        ucsc_synonym='hg38',
        api_last_updated='2019-02-28'
    )
    return trackhubs.models.GenomeAssemblyDump.objects.bulk_create([hg19_dump, hg38_dump])


@pytest.fixture()
def create_trackhub_resource(
    api_client,
    create_user_resource,
    create_datatype_resource,
    create_species_resource,
    create_filetype_resource,
    create_visibility_resource
):
    """
    Create a temporary trackhub and related trackdbs directly in DB
    to avoid external network dependencies during tests.
    """
    user, token = create_user_resource
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))

    data_type = create_datatype_resource

    hub_url = 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/hub.txt'
    hub = _create_hub(user=user, data_type=data_type, url=hub_url)

    assembly_37 = _create_assembly(
        accession='GCA_000001405.1',
        name='GRCh37',
        long_name='GRCh37',
        ucsc_synonym='hg19'
    )
    assembly_38 = _create_assembly(
        accession='GCA_000001405.15',
        name='GRCh38',
        long_name='GRCh38',
        ucsc_synonym='hg38'
    )

    species = create_species_resource

    trackdb_url = 'https://raw.githubusercontent.com/Ensembl/thr/master/samples/JASPAR_TFBS/trackDb.txt'
    _create_trackdb(hub=hub, assembly=assembly_37, species=species, source_url=trackdb_url)
    trackdb_38 = _create_trackdb(hub=hub, assembly=assembly_38, species=species, source_url=trackdb_url)

    # Create two tracks for assembly_38 to satisfy tracks_per_assembly tests.
    _create_track(
        trackdb=trackdb_38,
        file_type=create_filetype_resource,
        visibility=create_visibility_resource,
        name='track_one',
        short_label='Track One',
        long_label='Track One Long',
        big_data_url='http://example.org/track_one.bb'
    )
    _create_track(
        trackdb=trackdb_38,
        file_type=create_filetype_resource,
        visibility=create_visibility_resource,
        name='track_two',
        short_label='Track Two',
        long_label='Track Two Long',
        big_data_url='http://example.org/track_two.bb'
    )

    return hub


@pytest.fixture()
def create_hub_resource(create_user_resource, create_datatype_resource):
    """
    Create a temporary hub object
    """
    user, _ = create_user_resource
    return _create_hub(
        user=user,
        data_type=trackhubs.models.DataType.objects.filter(name=create_datatype_resource.name).first(),
        url='https://url/to/the/hub.txt'
    )


@pytest.fixture()
def create_assembly_resource():
    """
    Create a temporary assembly object
    """
    return _create_assembly(accession='GCA_000001405.1', name='GRCh37', long_name='', ucsc_synonym='')


@pytest.fixture()
def create_trackdb_resource(create_hub_resource, create_assembly_resource, create_species_resource):
    """
    Create a temporary trackdb object
    """
    trackdb_url = 'http://some.random/url/for/trackDb.txt'

    return _create_trackdb(
        hub=create_hub_resource,
        assembly=create_assembly_resource,
        species=create_species_resource,
        source_url=trackdb_url
    )


@pytest.fixture()
def create_track_resource(create_trackdb_resource, create_filetype_resource, create_visibility_resource):
    """
    Create a temporary track object
    """
    return _create_track(
        trackdb=create_trackdb_resource,
        file_type=trackhubs.models.FileType.objects.filter(name='bam').first(),
        visibility=trackhubs.models.Visibility.objects.filter(name='pack').first(),
        name='JASPAR2020_TFBS_hg19',
        short_label='JASPAR2020 TFBS hg19',
        long_label='TFBS predictions for all profiles in the JASPAR CORE vertebrates collection (2020)',
        big_data_url='http://path.to/the/track/bigbed/file/JASPAR2020_hg19.bb'
    )


@pytest.fixture()
def create_child_track_resource(create_trackdb_resource, create_filetype_resource, create_visibility_resource,
                                create_track_resource):
    """
    Create a temporary track object which is the child of another track
    this parent track is empty, it is used to test add_parent_id() function
    """
    return _create_track(
        trackdb=create_trackdb_resource,
        file_type=trackhubs.models.FileType.objects.filter(name='bam').first(),
        visibility=trackhubs.models.Visibility.objects.filter(name='pack').first(),
        name='Child track name',
        short_label='child of JASPAR2020',
        long_label='This is the child of the track described as follows: TFBS predictions for all profiles in the '
                   'JASPAR CORE vertebrates collection (2020)',
        big_data_url='http://path.to/the/subtrack/bigbed/file/JASPAR2020_hg19_subtrack.bb'
    )


@pytest.fixture()
def create_child_track_with_parent_resource(create_trackdb_resource, create_filetype_resource,
                                            create_visibility_resource, create_track_resource):
    """
    Create a temporary track object which is the child of another track
    this parent track is provided, it is used to test get_parents() function
    """
    return _create_track(
        trackdb=create_trackdb_resource,
        file_type=trackhubs.models.FileType.objects.filter(name='bam').first(),
        visibility=trackhubs.models.Visibility.objects.filter(name='pack').first(),
        name='Child track name',
        short_label='child of JASPAR2020',
        long_label='This is the child of the track described as follows: TFBS predictions for all profiles in the '
                   'JASPAR CORE vertebrates collection (2020)',
        big_data_url='http://path.to/the/subtrack/bigbed/file/JASPAR2020_hg19_subtrack.bb',
        parent=create_track_resource
    )
