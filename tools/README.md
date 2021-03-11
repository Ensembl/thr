## Check hub settings using hubCheck utility

In this folder will reside the `hubCheck` utility used to check that the files in the submitted hub are correctly formatted.

Here is the usage statement for the hubCheck utility:

```shell
hubCheck - Check a track data hub for integrity.
usage:
   hubCheck http://yourHost/yourDir/hub.txt
options:
   -checkSettings        - check trackDb settings to spec
   -version=[v?|url]     - version to validate settings against
                                     (defaults to version in hub.txt, or current standard)
   -extra=[file|url]     - accept settings in this file (or url)
   -level=base|required  - reject settings below this support level
   -settings             - just list settings with support level
                           Will create this directory if not existing
   -noTracks             - don't check remote files for tracks, just trackDb (faster)
   -udcDir=/dir/to/cache - place to put cache for remote bigBeds and bigWigs
```

More details can be found [here](https://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html#Debug).