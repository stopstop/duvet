# Duvet - The Missing Torrent Site Search Aggregator
The idea behind Duvet is simple. There are a bunch of applications all
recreating the wheel building their own search engines for various 
torrent sites. When those sites change something that breaks the 
parsing, everyone needs to update their code in hundreds of places. 

We're all reinventing the wheel repeatedly.

*We need to stop*. Let's work together and build a pip 
installable/upgradable solution that works for everyone.


## Sites Searched
* Bitsnoop
* Bit Torrent Scene
* Extratorrent
* EZTV
* 13376
* RARBG
* The Pirate Bay
* Torrent Downloads (disabled because dodgy data)

# CLI Usage with Blanket
<pre>
$ python3 blanket.py --search 'Game of Thrones' --season=5 --episode=9

$ python3 blanket.py --search 'UFC 202' --min-seeders=2000

$ python3 blanket.py --search 'Something Obscure' --show=15

$ python3 blanket.py --help
Usage: blanket.py [OPTIONS]

Options:
  --search TEXT          What would you like to search for?
  --season INTEGER       Season Number.
  --episode INTEGER      Episode Number.
  --min-seeders INTEGER  Minimum number of seeders.
  --show INTEGER         How many results to show.
  --help                 Show this message and exit.
</pre>

# Code Usage
## Searching for a specific string
<pre>
import duvet
d = duvet.Duvet()
results = d.search('UFC 202', min_seeders=1000)
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
import duvet
d = duvet.Duvet()
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


# TODO: 
* Unit Tests.
* Move everything over the the Requests library.
* Abstract the HTTP calls into a shared method.
* Optionally implement the Retrying library.
* Tests to validate that the various searches are working. (perhaps
something that uses tvdb to verify that we have results for things
yesterday, today, last week etc. 
* Better tools for discovering non-episodic things (documentaries etc).
* Elegant exception handling. Current approach is "fail brutally so we 
know what to fix".
* Timing and meta data on the search response. (eg. "9 websites 
searched, talked to 12 domains, 8 responded, 42 results found, 38 
duplicates removed, 12 results with too few seeders, query took 
3.2 seconds.")
* Start tackling the list of providers from 
https://github.com/SickRage/SickRage/tree/master/sickbeard/providers so
that we can get parity.
* Remove onethreethreesevenx_to's reliance on the very slow to load
"dateparser".


# Quickstart
* Duvet uses Python3. (```apt-get install python3``` or 
```brew install python3```)
* Duvet uses various pip installable packages (```pip3 install -r 
requirements.txt```)
* You can pip install the repo locally (It's not on pypi yet) by 
running ```pip install .``` or ```pip install -e .``` install the 
package with a symlink, so that changes to the source files will be 
immediately available to other users of the package on our system: 


# Thanks
Duvet is based on a lot of original code from 
https://github.com/8cylinder/tv-overlord
