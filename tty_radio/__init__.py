BANNER = "~=radio tuner=~"

VOL = "11000"  # volume 0 .. 32k

# CSV file format
# <stream URL>,<stream name>,<stream_img_url>
SOMA_CHAN_FILENAME = ".somachannels.csv"
# maximum age of the channel file before rebuilding it
CHAN_AGE_LIMIT = 7  # in days
FAVS_CHAN_FILENAME = ".favchannels.csv"  # manually updated
# Here is the default/recommended .favchannels.csv:
FAVS_DEFAULT = """
http://www.ibiblio.org/wcpe/wcpe.pls,WCPE Classical,"TheClassicalStation.org from Wake Forest, NC",http://theclassicalstation.org/images/wcpe_footer.jpg
http://ice.somafm.com/defcon,DEF CON Radio,Music for Hacking,http://somafm.com/img/defcon120.png
http://ice.somafm.com/groovesalad,Groove Salad,Nice chill plate of ambient/downtempo beats and grooves,http://somafm.com/img/groovesalad120.png
http://broadcast.wnrn.org:8000/wnrn.mp3,WNRN Cville,"Charlottesville, VA Independent Radio",http://www.wnrn.org/wp-content/themes/WNRN/images/logo2.gif
http://ice.somafm.com/bagel,BAGeL Radio,What alternative rock radio should sound like,http://somafm.com/img/bagel120.png
http://ice.somafm.com/folkfwd,Folk Forward,"Indie, Alt, and Classic folk",http://somafm.com/img/folkfwd120.jpg
http://ice.somafm.com/lush,Lush,"Electronica with sensuous/mellow vocals, mostly female",http://somafm.com/img/lush-x120.jpg
http://ice.somafm.com/suburbsofgoa,Suburbs of Goa,Desi-influenced Asian world beats and beyond,http://somafm.com/img/sog120.jpg
http://ice.somafm.com/u80s,Underground 80s,Early 80s UK Synthpop and a bit of New Wave,http://somafm.com/img/u80s-120.png
"""  # noqa

# page to parse for channel urls, names, and descriptions
SOMA_PARSE_URL = "http://somafm.com"
####
# format of stream url
# original py script template: http://ice.somafm.com/<NAME>
# but that isn't doc'ed on soma's site anywhere
# what is the preferred/polite link?
# from: http://somafm.com/lush/directstreamlinks.html:
#   http://somafm.com/<NAME>.pls  for 128 Kb
#   http://somafm.com/<NAME>24.pls  for 24 Kb
#   but this doesn't load in mpg123 at all
# from other links on somafm site:
#   http://somafm.com/play/<NAME>
#   but this doesn't load in mpg123 at all
# mpg123 can handle the "direct links", but to parse for these would
# require requesting each channel's directstreamlinks.html
SOMA_STREAM_BASE_URL = "http://ice.somafm.com/"
SOMA_STREAM_END_URL  = ""

# If true, then station will only show most recent song title
COMPACT_TITLES = True
"""
  ###       ###              ###                 ###     ####
 ## #        ##               ##                 #      ##  #
 ##    # ##  ###   # ## ## #  ###   ###    ##  ####    ##      ##   ###
  ##  ## ## ## ## ## ##  ### ## ## ###    ## #  ##     ## ### ## #   ###
# ##  ## #  ## #  ## #  ##   ## #    ##   #  #  ##     ## ##  #  # ## #
###    ####  ##    #### ##    ##   ###     ##   ##      ## #   ##   ####
                                                #
                                               #

>>> Suburbs of Goa: Desi-influenced Asian world beats. [SomaFM]
>>> Karsh Kale - Satellite
"""
# If false, then station will show history
"""
>>> Suburbs of Goa: Desi-influenced Asian world beats. [SomaFM]
>>> David Starfire - Sitarfire
>>> Karsh Kale - Satellite
"""
