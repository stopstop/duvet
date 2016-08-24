# Duvet - The Missing Torrent Site Search Aggregator

Based on a lot of code from https://github.com/8cylinder/tv-overlord

# Usage
## Searching for a specific string
<pre>
results = duvet.search('UFC 202', min_seeders=1000)
for r in results:
    print(r)
</pre>

### Output
<pre>
UFC 202 PPV Diaz vs McGregor HDTV x264-FMN [TJET]              Size: 1.86 GB        Seeders: 31388    Age: 1 days   EXT
UFC 202 PPV Diaz vs McGregor 720p HDTV x264-FMN [TJET]         Size: 5.12 GB        Seeders: 29627    Age: 1 days   EXT
UFC 202 HDTV x264-LiNKLE [TJET]                                Size: 1.69 GB        Seeders: 11447    Age: 1 days   EXT
UFC 202 Preliminary Fights 720p HDTV x264-KYR [TJET]           Size: 2.64 GB        Seeders: 7260     Age: 1 days   EXT
UFC 201 PPV Lawler vs Woodley HDTV x264-FMN [TJET]             Size: 1.78 GB        Seeders: 6581     Age: 22 days   EXT
UFC 202 Early Prelims WEB-DL H264 Fight-BB                     Size: 1.05 GB        Seeders: 5793     Age: 1 days   EXT
UFC 202 HDTV x264-Nada[state]                                  Size: 860.45 MB      Seeders: 5006     Age: 1 days   EXT
UFC 202 -Diaz Vs McGregor 2 2016/20/8 720p PPV HDTV [Love Ru   Size: 2.50 GB        Seeders: 4683     Age: 1 days   TPB
UFC 202 Early Prelims 720p WEB-DL H264 Fight-BB                Size: 3.01 GB        Seeders: 4652     Age: 1 days   EXT
UFC202 PPV Diaz vs McGregor 720p HDTV x264-FMN [TJET]1         Size: 4.77 GB        Seeders: 4504     Age: 1 days   13X
UFC Fight Night 92 Rodriguez vs Caceres HDTV x264-Ebi [TJET]   Size: 2.30 GB        Seeders: 4462     Age: 15 days   EXT
UFC202 PPV Diaz vs McGregor HDTV x264-FMN [TJET]2              Size: 1.74 GB        Seeders: 4294     Age: 1 days   13X
UFC 202 Prelims HDTV x264-LiNKLE [TJET]                        Size: 975.30 MB      Seeders: 4039     Age: 1 days   EXT
UFC Fight Night 92 Prelims HDTV x264-Ebi [TJET]                Size: 1.12 GB        Seeders: 3920     Age: 15 days   EXT
UFC200 PPV Lesnar vs Hunt HDTV x264-FMN [TJET]                 Size: 2.07 GB        Seeders: 3487     Age: 31 days   13X
UFC..202.PPV.Diaz.vs.McGregor.HDTV.x264-FMN.mp4                Size: 1.86 GB        Seeders: 3153     Age: 1 days   EXT
UFC 201 Prelims HDTV x264-Ebi [TJET]                           Size: 1.03 GB        Seeders: 3083     Age: 22 days   EXT
</pre>

## Searching for an episode
<pre>
results = duvet.search('Stranger Things', season=1, episode=3, min_seeders=100)
for r in results:
    print(r)
</pre>

### Output
<pre>
Stranger.Things.S01E03.WEBRip.x264-TURBO[ettv]                 Size: 281.09 MB      Seeders: 15504    Age: 38 days   EXT
Stranger.Things.S01E03.720p.WEBRip.x264-SKGTV[ettv]            Size: 1.34 GB        Seeders: 1277     Age: 38 days   EXT
Stranger Things S01E03 WEBRip x264-TURBO mkv                   Size: 281.09 MB      Seeders: 554      Age: Unknown   BTS
Stranger Things S01E03 WEBRip x264-TURBO [eztv]                Size: 268.07 MB      Seeders: 533      Age: 28 days   EZT
Stranger.Things.S01E03.720p.WEBRip.x264-SKGTV[ettv]            Size: 1.25 GB        Seeders: 307      Age: 38 days   BTR
Stranger Things S01E03 WebRip x264 mp4-FS                      Size: 274.64 MB      Seeders: 199      Age: 38 days   EXT
Stranger.Things.S01E03.720p.WEBRip.x264-SKGTV[PRiME]           Size: 1.34 GB        Seeders: 194      Age: 38 days   EXT
Stranger.Things.S01E03.720p.WEBRip.x264-SKGTV[rartv]           Size: 1.34 GB        Seeders: 190      Age: 38 days   RBG
</pre>

