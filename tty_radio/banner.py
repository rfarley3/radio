from __future__ import print_function
from random import choice
from io import StringIO
PYFIG = True
try:
    from pyfiglet import Figlet, FontNotFound
except ImportError:
    PYFIG = False
    print("Hey-o, you don't have ascii art banner libs installed:")
    print("  pip install pyfiglet")
"""
cd pyfiglet-master
ls -l pyfiglet/fonts/ | \
  grep -v '^total' | grep -v py$ | \
  sed -e "s/.*:33 /, '/" | sed  -e "s/_*.flf.*/'/" | \
  paste -s -d" " -

fonts = ['1943', '3-d', '3x5', '4x4_offr', '5lineoblique', '5x7', '64f1', '6x10', '6x9', 'a_zooloo', 'acrobatic', 'advenger', 'alligator', 'alligator2', 'alphabet', 'aquaplan', 'ascii', 'assalt_m', 'asslt__m', 'atc', 'atc_gran', 'avatar', 'banner', 'banner3-D', 'banner3', 'banner4', 'barbwire', 'basic', 'battle_s', 'battlesh', 'baz__bil', 'beer_pub', 'bell', 'big', 'bigchief', 'binary', 'block', 'brite', 'briteb', 'britebi', 'britei', 'broadway', 'bubble', 'bubble', 'bubble_b', 'bulbhead', 'c1', 'c2', 'c_ascii', 'c_consen', 'calgphy2', 'caligraphy', 'catwalk', 'caus_in', 'char1', 'char2', 'char3', 'char4', 'charact1', 'charact2', 'charact3', 'charact4', 'charact5', 'charact6', 'characte', 'charset', 'chartr', 'chartri', 'chunky', 'clb6x10', 'clb8x10', 'clb8x8', 'cli8x8', 'clr4x6', 'clr5x10', 'clr5x6', 'clr5x8', 'clr6x10', 'clr6x6', 'clr6x8', 'clr7x10', 'clr7x8', 'clr8x10', 'clr8x8', 'coil_cop', 'coinstak', 'colossal', 'com_sen', 'computer', 'contessa', 'contrast', 'convoy', 'cosmic', 'cosmike', 'cour', 'courb', 'courbi', 'couri', 'crawford', 'cricket', 'cursive', 'cyberlarge', 'cybermedium', 'cybersmall', 'd_dragon', 'dcs_bfmo', 'decimal', 'deep_str', 'demo_1', 'demo_2', 'demo_m', 'devilish', 'diamond', 'digital', 'doh', 'doom', 'dotmatrix', 'double', 'drpepper', 'druid', 'dwhistled', 'e__fist', 'ebbs_1', 'ebbs_2', 'eca', 'eftichess', 'eftifont', 'eftipiti', 'eftirobot', 'eftitalic', 'eftiwall', 'eftiwater', 'epic', 'etcrvs', 'f15', 'faces_of', 'fair_mea', 'fairligh', 'fbr12', 'fbr1', 'fbr2', 'fbr_stri', 'fbr_tilt', 'fender', 'finalass', 'fireing', 'flyn_sh', 'fourtops', 'fp2', 'fraktur', 'funky_dr', 'future_1', 'future_2', 'future_3', 'future_4', 'future_5', 'future_6', 'future_7', 'future_8', 'fuzzy', 'gauntlet', 'ghost_bo', 'goofy', 'gothic', 'gothic', 'graceful', 'gradient', 'graffiti', 'grand_pr', 'green_be', 'hades', 'heavy_me', 'helv', 'helvb', 'helvbi', 'helvi', 'heroboti', 'hex', 'high_noo', 'hills', 'hollywood', 'home_pak', 'house_of', 'hypa_bal', 'hyper', 'inc_raw', 'invita', 'isometric1', 'isometric2', 'isometric3', 'isometric4', 'italic', 'italics', 'ivrit', 'jazmine', 'jerusalem', 'joust', 'kban', 'kgames_i', 'kik_star', 'krak_out', 'larry3d', 'lazy_jon', 'lcd', 'lean', 'letter_w', 'letters', 'letterw3', 'linux', 'lockergnome', 'mad_nurs', 'madrid', 'magic_ma', 'marquee', 'master_o', 'maxfour', 'mayhem_d', 'mcg', 'mig_ally', 'mike', 'mini', 'mirror', 'mnemonic', 'modern', 'morse', 'moscow', 'mshebrew210', 'nancyj-fancy', 'nancyj-underlined', 'nancyj', 'new_asci', 'nfi1', 'nipples', 'notie_ca', 'ntgreek', 'nvscript', 'o8', 'octal', 'odel_lak', 'ogre', 'ok_beer', 'os2', 'p_s_h_m', 'p_skateb', 'pacos_pe', 'panther', 'pawn_ins', 'pawp', 'peaks', 'pebbles', 'pepper', 'phonix', 'platoon2', 'platoon', 'pod', 'poison', 'puffy', 'pyramid', 'r2-d2', 'rad', 'rad_phan', 'radical', 'rainbow', 'rally_s2', 'rally_sp', 'rastan', 'raw_recu', 'rci', 'rectangles', 'relief', 'relief2', 'rev', 'ripper!', 'road_rai', 'rockbox', 'rok', 'roman', 'roman', 'rot13', 'rounded', 'rowancap', 'rozzo', 'runic', 'runyc', 'sans', 'sansb', 'sansbi', 'sansi', 'sblood', 'sbook', 'sbookb', 'sbookbi', 'sbooki', 'script', 'script', 'serifcap', 'shadow', 'short', 'skate_ro', 'skateord', 'skateroc', 'sketch_s', 'slant', 'slide', 'slscript', 'sm', 'small', 'smisome1', 'smkeyboard', 'smscript', 'smshadow', 'smslant', 'smtengwar', 'speed', 'stacey', 'stampatello', 'standard', 'star_war', 'starwars', 'stealth', 'stellar', 'stencil1', 'stencil2', 'stop', 'straight', 'street_s', 'subteran', 'super_te', 't__of_ap', 'tanja', 'tav1', 'taxi', 'tec1', 'tec_7000', 'tecrvs', 'tengwar', 'term', 'thick', 'thin', 'threepoint', 'ti_pan', 'ticks', 'ticksslant', 'times', 'timesofl', 'tinker-toy', 'tomahawk', 'tombstone', 'top_duck', 'trashman', 'trek', 'triad_st', 'tsalagi', 'tsm', 'tsn_base', 'tty', 'ttyb', 'twin_cob', 'twopoint', 'type_set', 'ucf_fan', 'ugalympi', 'unarmed', 'univers', 'usa', 'usa_pq', 'usaflag', 'utopia', 'utopiab', 'utopiabi', 'utopiai', 'vortron', 'war_of_w', 'weird', 'whimsy', 'xbrite', 'xbriteb', 'xbritebi', 'xbritei', 'xchartr', 'xchartri', 'xcour', 'xcourb', 'xcourbi', 'xcouri', 'xhelv', 'xhelvb', 'xhelvbi', 'xhelvi', 'xsans', 'xsansb', 'xsansbi', 'xsansi', 'xsbook', 'xsbookb', 'xsbookbi', 'xsbooki', 'xtimes', 'xtty', 'xttyb', 'yie-ar', 'yie_ar_k', 'z-pilot', 'zig_zag']  # noqa

nerdy_but_unpretty = [ 'hex', 'octal', 'binary', 'rot13', 'morse' ]
"""


# here are the fonts that I find the most interesting:
FONTS = ['3-d', '3x5', '5lineoblique', 'a_zooloo', 'acrobatic', 'alligator', 'alligator2', 'alphabet', 'avatar', 'banner', 'banner3-D', 'banner4', 'barbwire', 'basic', 'bell', 'big', 'bigchief', 'block', 'britebi', 'broadway', 'bubble', 'bulbhead', 'calgphy2', 'caligraphy', 'catwalk', 'charact1', 'charact4', 'chartri', 'chunky', 'clb6x10', 'coinstak', 'colossal', 'computer', 'contessa', 'contrast', 'cosmic', 'cosmike', 'courbi', 'crawford', 'cricket', 'cursive', 'cyberlarge', 'cybermedium', 'cybersmall', 'devilish', 'diamond', 'digital', 'doh', 'doom', 'dotmatrix', 'double', 'drpepper', 'dwhistled', 'eftichess', 'eftifont', 'eftipiti', 'eftirobot', 'eftitalic', 'eftiwall', 'eftiwater', 'epic', 'fender', 'fourtops', 'fraktur', 'funky_dr', 'fuzzy', 'goofy', 'gothic', 'graceful', 'graffiti', 'helvbi', 'hollywood', 'home_pak', 'invita', 'isometric1', 'isometric2', 'isometric3', 'isometric4', 'italic', 'ivrit', 'jazmine', 'jerusalem', 'kban', 'larry3d', 'lean', 'letters', 'linux', 'lockergnome', 'madrid', 'marquee', 'maxfour', 'mike', 'mini', 'mirror', 'moscow', 'mshebrew210', 'nancyj-fancy', 'nancyj-underlined', 'nancyj', 'new_asci', 'nipples', 'ntgreek', 'nvscript', 'o8', 'odel_lak', 'ogre', 'os2', 'pawp', 'peaks', 'pebbles', 'pepper', 'poison', 'puffy', 'rectangles', 'relief', 'relief2', 'rev', 'roman', 'rounded', 'rowancap', 'rozzo', 'runic', 'runyc', 'sansbi', 'sblood', 'sbookbi', 'script', 'serifcap', 'shadow', 'short', 'sketch_s', 'slant', 'slide', 'slscript', 'small', 'smisome1', 'smkeyboard', 'smscript', 'smshadow', 'smslant', 'smtengwar', 'speed', 'stacey', 'stampatello', 'standard', 'starwars', 'stellar', 'stop', 'straight', 't__of_ap', 'tanja', 'tengwar', 'thick', 'thin', 'threepoint', 'ticks', 'ticksslant', 'tinker-toy', 'tombstone', 'trek', 'tsalagi', 'twin_cob', 'twopoint', 'univers', 'usaflag', 'utopiabi', 'weird', 'whimsy', 'xbritebi', 'xcourbi']  # noqa


def rand_font():
    # built-in font fetch doesn't work:
    #   fonts = f.getFonts()
    # do 100 tries in case font doesn't exist
    # if there are 100 failures, bannerize will fail/barf
    #   on its Figlet constructor
    for i in range(100):
        fi = choice(FONTS)
        try:
            Figlet(font=fi)
            return fi
        except FontNotFound:
            continue
    return "none"


def bannerize(str, term_w):
    # do 100 attempts to find a suitable font
    # criteria:
    #   must be narrower than term window
    #   wider than 1/4 the term window(the larger, the prettier)
    out = "\n" + str + "\n" + '-' * len(str) + "\n"
    fi = "none"
    if not PYFIG:
        return (out, fi)
    for i in range(100):
        fi = rand_font()
        f = Figlet(font=fi, width=term_w)
        out = f.renderText(str)
        out_IO = StringIO(out)
        out_width = max([len(a) for a in out_IO.readlines()])
        # print("outWidth: %d"%outWidth)
        if out_width <= term_w and out_width > (term_w / 4):
            # print("Font name: " + fi)
            return (out, fi)
    return (out, fi)
