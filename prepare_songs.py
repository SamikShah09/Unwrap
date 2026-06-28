import json
import shutil
import subprocess
import sys
import requests
from pathlib import Path

def check_dependencies():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[ERROR] ffmpeg is not installed or not in your PATH.")
        print("Please install ffmpeg:")
        print("  Windows: winget install ffmpeg  (or download from gyan.dev)")
        print("  Mac:     brew install ffmpeg")
        print("  Linux:   sudo apt install ffmpeg")
        sys.exit(1)

    missing = []
    for pkg in ["demucs", "pydub", "requests"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"[ERROR] Missing Python packages: {', '.join(missing)}")
        print("Please run: pip install " + " ".join(missing))
        sys.exit(1)

check_dependencies()

SONGS = [
    {
        "title":   "Blinding Lights",
        "artists": ["The Weeknd"],
        "id":      "blinding_lights"
    },
    {
        "title":   "Shape of You",
        "artists": ["Ed Sheeran"],
        "id":      "shape_of_you"
    },
    {
        "title":   "Sweater Weather",
        "artists": ["The Neighbourhood"],
        "id":      "sweater_weather"
    },
    {
        "title":   "Starboy",
        "artists": ["The Weeknd"],
        "id":      "starboy"
    },
    {
        "title":   "As It Was",
        "artists": ["Harry Styles"],
        "id":      "as_it_was"
    },
    {
        "title":   "Someone You Loved",
        "artists": ["Lewis Capaldi"],
        "id":      "someone_you_loved"
    },
    {
        "title":   "One Dance",
        "artists": ["Drake"],
        "id":      "one_dance"
    },
    {
        "title":   "Sunflower",
        "artists": ["Post Malone"],
        "id":      "sunflower"
    },
    {
        "title":   "Perfect",
        "artists": ["Ed Sheeran"],
        "id":      "perfect"
    },
    {
        "title":   "STAY",
        "artists": ["The Kid LAROI"],
        "id":      "stay"
    },
    {
        "title":   "Believer",
        "artists": ["Imagine Dragons"],
        "id":      "believer"
    },
    {
        "title":   "I Wanna Be Yours",
        "artists": ["Arctic Monkeys"],
        "id":      "i_wanna_be_yours"
    },
    {
        "title":   "Yellow",
        "artists": ["Coldplay"],
        "id":      "yellow"
    },
    {
        "title":   "Heat Waves",
        "artists": ["Glass Animals"],
        "id":      "heat_waves"
    },
    {
        "title":   "BIRDS OF A FEATHER",
        "artists": ["Billie Eilish"],
        "id":      "birds_of_a_feather"
    },
    {
        "title":   "The Night We Met",
        "artists": ["Lord Huron"],
        "id":      "the_night_we_met"
    },
    {
        "title":   "lovely",
        "artists": ["Billie Eilish"],
        "id":      "lovely"
    },
    {
        "title":   "Die With A Smile",
        "artists": ["Lady Gaga"],
        "id":      "die_with_a_smile"
    },
    {
        "title":   "Closer",
        "artists": ["The Chainsmokers"],
        "id":      "closer"
    },
    {
        "title":   "Riptide",
        "artists": ["Vance Joy"],
        "id":      "riptide"
    },
    {
        "title":   "Something Just Like This",
        "artists": ["The Chainsmokers"],
        "id":      "something_just_like_this"
    },
    {
        "title":   "Say You Won't Let Go",
        "artists": ["James Arthur"],
        "id":      "say_you_won_t_let_go"
    },
    {
        "title":   "Another Love",
        "artists": ["Tom Odell"],
        "id":      "another_love"
    },
    {
        "title":   "Every Breath You Take",
        "artists": ["The Police"],
        "id":      "every_breath_you_take"
    },
    {
        "title":   "Counting Stars",
        "artists": ["OneRepublic"],
        "id":      "counting_stars"
    },
    {
        "title":   "Take Me to Church",
        "artists": ["Hozier"],
        "id":      "take_me_to_church"
    },
    {
        "title":   "Iris",
        "artists": ["The Goo Goo Dolls"],
        "id":      "iris"
    },
    {
        "title":   "Photograph",
        "artists": ["Ed Sheeran"],
        "id":      "photograph"
    },
    {
        "title":   "Dance Monkey",
        "artists": ["Tones And I"],
        "id":      "dance_monkey"
    },
    {
        "title":   "rockstar",
        "artists": ["Post Malone"],
        "id":      "rockstar"
    },
    {
        "title":   "Cruel Summer",
        "artists": ["Taylor Swift"],
        "id":      "cruel_summer"
    },
    {
        "title":   "Can't Hold Us",
        "artists": ["Macklemore"],
        "id":      "can_t_hold_us"
    },
    {
        "title":   "Viva La Vida",
        "artists": ["Coldplay"],
        "id":      "viva_la_vida"
    },
    {
        "title":   "Señorita",
        "artists": ["Shawn Mendes"],
        "id":      "se_orita"
    },
    {
        "title":   "Just the Way You Are",
        "artists": ["Bruno Mars"],
        "id":      "just_the_way_you_are"
    },
    {
        "title":   "Locked out of Heaven",
        "artists": ["Bruno Mars"],
        "id":      "locked_out_of_heaven"
    },
    {
        "title":   "Watermelon Sugar",
        "artists": ["Harry Styles"],
        "id":      "watermelon_sugar"
    },
    {
        "title":   "Die For You",
        "artists": ["The Weeknd"],
        "id":      "die_for_you"
    },
    {
        "title":   "Mr. Brightside",
        "artists": ["The Killers"],
        "id":      "mr_brightside"
    },
    {
        "title":   "That's What I Like",
        "artists": ["Bruno Mars"],
        "id":      "that_s_what_i_like"
    },
    {
        "title":   "Love Yourself",
        "artists": ["Justin Bieber"],
        "id":      "love_yourself"
    },
    {
        "title":   "Don't Start Now",
        "artists": ["Dua Lipa"],
        "id":      "don_t_start_now"
    },
    {
        "title":   "In the End",
        "artists": ["Linkin Park"],
        "id":      "in_the_end"
    },
    {
        "title":   "When I Was Your Man",
        "artists": ["Bruno Mars"],
        "id":      "when_i_was_your_man"
    },
    {
        "title":   "Bohemian Rhapsody",
        "artists": ["Queen"],
        "id":      "bohemian_rhapsody"
    },
    {
        "title":   "Circles",
        "artists": ["Post Malone"],
        "id":      "circles"
    },
    {
        "title":   "goosebumps",
        "artists": ["Travis Scott"],
        "id":      "goosebumps"
    },
    {
        "title":   "Lucid Dreams",
        "artists": ["Juice WRLD"],
        "id":      "lucid_dreams"
    },
    {
        "title":   "Thinking out Loud",
        "artists": ["Ed Sheeran"],
        "id":      "thinking_out_loud"
    },
    {
        "title":   "Wake Me Up",
        "artists": ["Avicii"],
        "id":      "wake_me_up"
    },
    {
        "title":   "Without Me",
        "artists": ["Eminem"],
        "id":      "without_me"
    },
    {
        "title":   "Shallow",
        "artists": ["Lady Gaga"],
        "id":      "shallow"
    },
    {
        "title":   "All Of Me",
        "artists": ["John Legend"],
        "id":      "all_of_me"
    },
    {
        "title":   "Let Me Love You",
        "artists": ["DJ Snake"],
        "id":      "let_me_love_you"
    },
    {
        "title":   "God's Plan",
        "artists": ["Drake"],
        "id":      "god_s_plan"
    },
    {
        "title":   "The Hills",
        "artists": ["The Weeknd"],
        "id":      "the_hills"
    },
    {
        "title":   "Stressed Out",
        "artists": ["Twenty One Pilots"],
        "id":      "stressed_out"
    },
    {
        "title":   "Demons",
        "artists": ["Imagine Dragons"],
        "id":      "demons"
    },
    {
        "title":   "Espresso",
        "artists": ["Sabrina Carpenter"],
        "id":      "espresso"
    },
    {
        "title":   "All The Stars",
        "artists": ["Kendrick Lamar"],
        "id":      "all_the_stars"
    },
    {
        "title":   "Thunder",
        "artists": ["Imagine Dragons"],
        "id":      "thunder"
    },
    {
        "title":   "Do I Wanna Know?",
        "artists": ["Arctic Monkeys"],
        "id":      "do_i_wanna_know"
    },
    {
        "title":   "Beautiful Things",
        "artists": ["Benson Boone"],
        "id":      "beautiful_things"
    },
    {
        "title":   "Seven",
        "artists": ["Jung Kook"],
        "id":      "seven"
    },
    {
        "title":   "See You Again",
        "artists": ["Tyler, The Creator"],
        "id":      "see_you_again"
    },
    {
        "title":   "Sorry",
        "artists": ["Justin Bieber"],
        "id":      "sorry"
    },
    {
        "title":   "Billie Jean",
        "artists": ["Michael Jackson"],
        "id":      "billie_jean"
    },
    {
        "title":   "Creep",
        "artists": ["Radiohead"],
        "id":      "creep"
    },
    {
        "title":   "Unforgettable",
        "artists": ["French Montana"],
        "id":      "unforgettable"
    },
    {
        "title":   "No Role Modelz",
        "artists": ["J. Cole"],
        "id":      "no_role_modelz"
    },
    {
        "title":   "Smells Like Teen Spirit",
        "artists": ["Nirvana"],
        "id":      "smells_like_teen_spirit"
    },
    {
        "title":   "Lose Yourself",
        "artists": ["Eminem"],
        "id":      "lose_yourself"
    },
    {
        "title":   "HUMBLE.",
        "artists": ["Kendrick Lamar"],
        "id":      "humble"
    },
    {
        "title":   "bad guy",
        "artists": ["Billie Eilish"],
        "id":      "bad_guy"
    },
    {
        "title":   "Clean Baby Sleep White Noise (Loopable)",
        "artists": ["Dream Supplier"],
        "id":      "clean_baby_sleep_white_noise_loopable"
    },
    {
        "title":   "Treat You Better",
        "artists": ["Shawn Mendes"],
        "id":      "treat_you_better"
    },
    {
        "title":   "Flowers",
        "artists": ["Miley Cyrus"],
        "id":      "flowers"
    },
    {
        "title":   "The Scientist",
        "artists": ["Coldplay"],
        "id":      "the_scientist"
    },
    {
        "title":   "505",
        "artists": ["Arctic Monkeys"],
        "id":      "505"
    },
    {
        "title":   "drivers license",
        "artists": ["Olivia Rodrigo"],
        "id":      "drivers_license"
    },
    {
        "title":   "There's Nothing Holdin' Me Back",
        "artists": ["Shawn Mendes"],
        "id":      "there_s_nothing_holdin_me_back"
    },
    {
        "title":   "Don't Stop Believin'",
        "artists": ["Journey"],
        "id":      "don_t_stop_believin"
    },
    {
        "title":   "7 rings",
        "artists": ["Ariana Grande"],
        "id":      "7_rings"
    },
    {
        "title":   "Wonderwall",
        "artists": ["Oasis"],
        "id":      "wonderwall"
    },
    {
        "title":   "Let Her Go",
        "artists": ["Passenger"],
        "id":      "let_her_go"
    },
    {
        "title":   "Kill Bill",
        "artists": ["SZA"],
        "id":      "kill_bill"
    },
    {
        "title":   "Take On Me",
        "artists": ["a-ha"],
        "id":      "take_on_me"
    },
    {
        "title":   "Dreams",
        "artists": ["Fleetwood Mac"],
        "id":      "dreams"
    },
    {
        "title":   "Numb",
        "artists": ["Linkin Park"],
        "id":      "numb"
    },
    {
        "title":   "Sweet Child O' Mine",
        "artists": ["Guns N' Roses"],
        "id":      "sweet_child_o_mine"
    },
    {
        "title":   "Save Your Tears",
        "artists": ["The Weeknd"],
        "id":      "save_your_tears"
    },
    {
        "title":   "Cold Heart",
        "artists": ["Elton John"],
        "id":      "cold_heart"
    },
    {
        "title":   "End of Beginning",
        "artists": ["Djo"],
        "id":      "end_of_beginning"
    },
    {
        "title":   "Payphone",
        "artists": ["Maroon 5"],
        "id":      "payphone"
    },
    {
        "title":   "One Kiss",
        "artists": ["Calvin Harris"],
        "id":      "one_kiss"
    },
    {
        "title":   "Lean On",
        "artists": ["Major Lazer"],
        "id":      "lean_on"
    },
    {
        "title":   "One Of The Girls",
        "artists": ["The Weeknd"],
        "id":      "one_of_the_girls"
    },
    {
        "title":   "Uptown Funk",
        "artists": ["Mark Ronson"],
        "id":      "uptown_funk"
    },
    {
        "title":   "Don't Stop Me Now",
        "artists": ["Queen"],
        "id":      "don_t_stop_me_now"
    },
    {
        "title":   "good 4 u",
        "artists": ["Olivia Rodrigo"],
        "id":      "good_4_u"
    },
    {
        "title":   "Africa",
        "artists": ["TOTO"],
        "id":      "africa"
    },
    {
        "title":   "We Don't Talk Anymore",
        "artists": ["Charlie Puth"],
        "id":      "we_don_t_talk_anymore"
    },
    {
        "title":   "Someone Like You",
        "artists": ["Adele"],
        "id":      "someone_like_you"
    },
    {
        "title":   "Happier",
        "artists": ["Marshmello"],
        "id":      "happier"
    },
    {
        "title":   "Danza Kuduro",
        "artists": ["Don Omar"],
        "id":      "danza_kuduro"
    },
    {
        "title":   "Night Changes",
        "artists": ["One Direction"],
        "id":      "night_changes"
    },
    {
        "title":   "LA CANCIÓN",
        "artists": ["J Balvin"],
        "id":      "la_canci_n"
    },
    {
        "title":   "Levitating",
        "artists": ["Dua Lipa"],
        "id":      "levitating"
    },
    {
        "title":   "SICKO MODE",
        "artists": ["Travis Scott"],
        "id":      "sicko_mode"
    },
    {
        "title":   "Somewhere Only We Know",
        "artists": ["Keane"],
        "id":      "somewhere_only_we_know"
    },
    {
        "title":   "Everybody Wants To Rule The World",
        "artists": ["Tears For Fears"],
        "id":      "everybody_wants_to_rule_the_world"
    },
    {
        "title":   "New Rules",
        "artists": ["Dua Lipa"],
        "id":      "new_rules"
    },
    {
        "title":   "We Found Love",
        "artists": ["Calvin Harris"],
        "id":      "we_found_love"
    },
    {
        "title":   "Gangsta's Paradise",
        "artists": ["Coolio"],
        "id":      "gangsta_s_paradise"
    },
    {
        "title":   "Hips Don't Lie",
        "artists": ["Shakira"],
        "id":      "hips_don_t_lie"
    },
    {
        "title":   "7 Years",
        "artists": ["Lukas Graham"],
        "id":      "7_years"
    },
    {
        "title":   "SAD!",
        "artists": ["XXXTENTACION"],
        "id":      "sad"
    },
    {
        "title":   "Lose Control",
        "artists": ["Teddy Swims"],
        "id":      "lose_control"
    },
    {
        "title":   "XO Tour Llif3",
        "artists": ["Lil Uzi Vert"],
        "id":      "xo_tour_llif3"
    },
    {
        "title":   "Without Me",
        "artists": ["Halsey"],
        "id":      "without_me"
    },
    {
        "title":   "Too Good At Goodbyes",
        "artists": ["Sam Smith"],
        "id":      "too_good_at_goodbyes"
    },
    {
        "title":   "Stay With Me",
        "artists": ["Sam Smith"],
        "id":      "stay_with_me"
    },
    {
        "title":   "Stitches",
        "artists": ["Shawn Mendes"],
        "id":      "stitches"
    },
    {
        "title":   "I'm Not The Only One",
        "artists": ["Sam Smith"],
        "id":      "i_m_not_the_only_one"
    },
    {
        "title":   "Attention",
        "artists": ["Charlie Puth"],
        "id":      "attention"
    },
    {
        "title":   "Till I Collapse",
        "artists": ["Eminem"],
        "id":      "till_i_collapse"
    },
    {
        "title":   "Mockingbird",
        "artists": ["Eminem"],
        "id":      "mockingbird"
    },
    {
        "title":   "Pumped Up Kicks",
        "artists": ["Foster The People"],
        "id":      "pumped_up_kicks"
    },
    {
        "title":   "when the party's over",
        "artists": ["Billie Eilish"],
        "id":      "when_the_party_s_over"
    },
    {
        "title":   "All I Want for Christmas Is You",
        "artists": ["Mariah Carey"],
        "id":      "all_i_want_for_christmas_is_you"
    },
    {
        "title":   "APT.",
        "artists": ["ROSÉ"],
        "id":      "apt"
    },
    {
        "title":   "DÁKITI",
        "artists": ["Bad Bunny"],
        "id":      "d_kiti"
    },
    {
        "title":   "Somebody That I Used To Know",
        "artists": ["Gotye"],
        "id":      "somebody_that_i_used_to_know"
    },
    {
        "title":   "Memories",
        "artists": ["Maroon 5"],
        "id":      "memories"
    },
    {
        "title":   "The Less I Know The Better",
        "artists": ["Tame Impala"],
        "id":      "the_less_i_know_the_better"
    },
    {
        "title":   "Jocelyn Flores",
        "artists": ["XXXTENTACION"],
        "id":      "jocelyn_flores"
    },
    {
        "title":   "Havana",
        "artists": ["Camila Cabello"],
        "id":      "havana"
    },
    {
        "title":   "The Real Slim Shady",
        "artists": ["Eminem"],
        "id":      "the_real_slim_shady"
    },
    {
        "title":   "Me Rehúso",
        "artists": ["Danny Ocean"],
        "id":      "me_reh_so"
    },
    {
        "title":   "Easy On Me",
        "artists": ["Adele"],
        "id":      "easy_on_me"
    },
    {
        "title":   "Blank Space",
        "artists": ["Taylor Swift"],
        "id":      "blank_space"
    },
    {
        "title":   "Before You Go",
        "artists": ["Lewis Capaldi"],
        "id":      "before_you_go"
    },
    {
        "title":   "I'm Yours",
        "artists": ["Jason Mraz"],
        "id":      "i_m_yours"
    },
    {
        "title":   "Apocalypse",
        "artists": ["Cigarettes After Sex"],
        "id":      "apocalypse"
    },
    {
        "title":   "Another One Bites The Dust",
        "artists": ["Queen"],
        "id":      "another_one_bites_the_dust"
    },
    {
        "title":   "Who",
        "artists": ["Jimin"],
        "id":      "who"
    },
    {
        "title":   "Have You Ever Seen The Rain",
        "artists": ["Creedence Clearwater Revival"],
        "id":      "have_you_ever_seen_the_rain"
    },
    {
        "title":   "La Bachata",
        "artists": ["Manuel Turizo"],
        "id":      "la_bachata"
    },
    {
        "title":   "I Took A Pill In Ibiza",
        "artists": ["Mike Posner"],
        "id":      "i_took_a_pill_in_ibiza"
    },
    {
        "title":   "See You Again",
        "artists": ["Wiz Khalifa"],
        "id":      "see_you_again"
    },
    {
        "title":   "Feel Good Inc",
        "artists": ["Gorillaz"],
        "id":      "feel_good_inc"
    },
    {
        "title":   "Call Out My Name",
        "artists": ["The Weeknd"],
        "id":      "call_out_my_name"
    },
    {
        "title":   "Lush Life",
        "artists": ["Zara Larsson"],
        "id":      "lush_life"
    },
    {
        "title":   "Maps",
        "artists": ["Maroon 5"],
        "id":      "maps"
    },
    {
        "title":   "Moonlight",
        "artists": ["XXXTENTACION"],
        "id":      "moonlight"
    },
    {
        "title":   "Kiss Me More",
        "artists": ["Doja Cat"],
        "id":      "kiss_me_more"
    },
    {
        "title":   "I'm Good (Blue)",
        "artists": ["David Guetta"],
        "id":      "i_m_good_blue"
    },
    {
        "title":   "Don't Let Me Down",
        "artists": ["The Chainsmokers"],
        "id":      "don_t_let_me_down"
    },
    {
        "title":   "The Nights",
        "artists": ["Avicii"],
        "id":      "the_nights"
    },
    {
        "title":   "Faded",
        "artists": ["Alan Walker"],
        "id":      "faded"
    },
    {
        "title":   "Rolling in the Deep",
        "artists": ["Adele"],
        "id":      "rolling_in_the_deep"
    },
    {
        "title":   "The Box",
        "artists": ["Roddy Ricch"],
        "id":      "the_box"
    },
    {
        "title":   "Shut Up and Dance",
        "artists": ["WALK THE MOON"],
        "id":      "shut_up_and_dance"
    },
    {
        "title":   "Why'd You Only Call Me When You're High?",
        "artists": ["Arctic Monkeys"],
        "id":      "why_d_you_only_call_me_when_you_re_high"
    },
    {
        "title":   "A Sky Full of Stars",
        "artists": ["Coldplay"],
        "id":      "a_sky_full_of_stars"
    },
    {
        "title":   "I Love You So",
        "artists": ["The Walters"],
        "id":      "i_love_you_so"
    },
    {
        "title":   "Summertime Sadness",
        "artists": ["Lana Del Rey"],
        "id":      "summertime_sadness"
    },
    {
        "title":   "Set Fire to the Rain",
        "artists": ["Adele"],
        "id":      "set_fire_to_the_rain"
    },
    {
        "title":   "traitor",
        "artists": ["Olivia Rodrigo"],
        "id":      "traitor"
    },
    {
        "title":   "Heather",
        "artists": ["Conan Gray"],
        "id":      "heather"
    },
    {
        "title":   "Dandelions",
        "artists": ["Ruth B."],
        "id":      "dandelions"
    },
    {
        "title":   "September",
        "artists": ["Earth, Wind & Fire"],
        "id":      "september"
    },
    {
        "title":   "Highway to Hell",
        "artists": ["AC/DC"],
        "id":      "highway_to_hell"
    },
    {
        "title":   "Congratulations",
        "artists": ["Post Malone"],
        "id":      "congratulations"
    },
    {
        "title":   "Sugar",
        "artists": ["Maroon 5"],
        "id":      "sugar"
    },
    {
        "title":   "Radioactive",
        "artists": ["Imagine Dragons"],
        "id":      "radioactive"
    },
    {
        "title":   "I Ain't Worried",
        "artists": ["OneRepublic"],
        "id":      "i_ain_t_worried"
    },
    {
        "title":   "INDUSTRY BABY",
        "artists": ["Lil Nas X"],
        "id":      "industry_baby"
    },
    {
        "title":   "I Like Me Better",
        "artists": ["LAUV"],
        "id":      "i_like_me_better"
    },
    {
        "title":   "Titanium",
        "artists": ["David Guetta"],
        "id":      "titanium"
    },
    {
        "title":   "deja vu",
        "artists": ["Olivia Rodrigo"],
        "id":      "deja_vu"
    },
    {
        "title":   "Ghost",
        "artists": ["Justin Bieber"],
        "id":      "ghost"
    },
    {
        "title":   "This Is What You Came For",
        "artists": ["Calvin Harris"],
        "id":      "this_is_what_you_came_for"
    },
    {
        "title":   "a thousand years",
        "artists": ["Christina Perri"],
        "id":      "a_thousand_years"
    },
    {
        "title":   "Ride",
        "artists": ["Twenty One Pilots"],
        "id":      "ride"
    },
    {
        "title":   "HIGHEST IN THE ROOM",
        "artists": ["Travis Scott"],
        "id":      "highest_in_the_room"
    },
    {
        "title":   "Me Porto Bonito",
        "artists": ["Bad Bunny"],
        "id":      "me_porto_bonito"
    },
    {
        "title":   "Chandelier",
        "artists": ["Sia"],
        "id":      "chandelier"
    },
    {
        "title":   "Dynamite",
        "artists": ["BTS"],
        "id":      "dynamite"
    },
    {
        "title":   "Livin' On A Prayer",
        "artists": ["Bon Jovi"],
        "id":      "livin_on_a_prayer"
    },
    {
        "title":   "Passionfruit",
        "artists": ["Drake"],
        "id":      "passionfruit"
    },
    {
        "title":   "Umbrella",
        "artists": ["Rihanna"],
        "id":      "umbrella"
    },
    {
        "title":   "Thunderstruck",
        "artists": ["AC/DC"],
        "id":      "thunderstruck"
    },
    {
        "title":   "Better Now",
        "artists": ["Post Malone"],
        "id":      "better_now"
    },
    {
        "title":   "greedy",
        "artists": ["Tate McRae"],
        "id":      "greedy"
    },
    {
        "title":   "Love The Way You Lie",
        "artists": ["Eminem"],
        "id":      "love_the_way_you_lie"
    },
    {
        "title":   "Sign of the Times",
        "artists": ["Harry Styles"],
        "id":      "sign_of_the_times"
    },
    {
        "title":   "Heathens",
        "artists": ["Twenty One Pilots"],
        "id":      "heathens"
    },
    {
        "title":   "Tití Me Preguntó",
        "artists": ["Bad Bunny"],
        "id":      "tit_me_pregunt"
    },
    {
        "title":   "thank u, next",
        "artists": ["Ariana Grande"],
        "id":      "thank_u_next"
    },
]


AUDIO_DIR    = Path("audio")
DATA_FILE    = Path("dataComp.json")
DEMUCS_MODEL = "htdemucs_6s" 

def get_itunes_preview(title: str, artist: str) -> str | None:
    params = {"term": f"{title} {artist}", "media": "music", "limit": 5}
    try:
        r = requests.get("https://itunes.apple.com/search", params=params, timeout=10)
        r.raise_for_status()
        for result in r.json().get("results", []):
            if result.get("previewUrl"):
                return result["previewUrl"]
    except Exception as e:
        print(f"    [WARN] iTunes error: {e}")
    return None

def download_file(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=30, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"    [WARN] Download error: {e}")
        return False

def run_demucs(input_path: Path, work_dir: Path) -> Path | None:
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", DEMUCS_MODEL,
        "-o", str(work_dir),
        str(input_path),
    ]
    print("    [INFO] Running Demucs (6-stem model) -- this takes 2-5 min per song...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"    [ERROR] Demucs failed:\n{result.stderr[-400:]}")
        return None

    stems_dir = work_dir / DEMUCS_MODEL / input_path.stem
    if stems_dir.exists() and any(stems_dir.glob("drums.*")):
        return stems_dir

    hits = list(work_dir.rglob("drums.wav")) + list(work_dir.rglob("drums.mp3"))
    if hits:
        return hits[0].parent

    print("    [ERROR] Could not find Demucs output folder.")
    return None

def mix_stems(stems_dir: Path, stem_names: list, out_path: Path) -> bool:
    from pydub import AudioSegment

    mixed = None
    for name in stem_names:
        for ext in ("wav", "mp3", "flac"):
            p = stems_dir / f"{name}.{ext}"
            if p.exists():
                seg = AudioSegment.from_file(str(p))
                mixed = seg if mixed is None else mixed.overlay(seg)
                break
        else:
            print(f"    [WARN] Stem '{name}' not found, skipping.")

    if mixed is None:
        return False

    mixed.export(str(out_path), format="mp3", bitrate="128k")
    print(f"    [OK] Created {out_path.name}")
    return True

def process_song(song: dict) -> dict | None:
    sid      = song["id"]
    title    = song["title"]
    artist   = song["artists"][0]
    song_dir = AUDIO_DIR / sid
    song_dir.mkdir(parents=True, exist_ok=True)

    stages = [
        song_dir / "stage1_drums.mp3",
        song_dir / "stage2_drums_bass.mp3",
        song_dir / "stage3_drums_bass_guitar.mp3",
        song_dir / "stage4_drums_bass_guitar_piano.mp3",
        song_dir / "stage5_drums_bass_guitar_piano_other.mp3",
        song_dir / "stage6_drums_bass_guitar_piano_other_vocals.mp3",
        song_dir / "stage7_full.mp3",
    ]

    if all(s.exists() for s in stages):
        print("    [SKIP] Already done, skipping.")
        return _build_entry(song, stages)

    raw = song_dir / "raw.m4a"
    if not raw.exists():
        print(f"    [INFO] Fetching preview for '{title}'...")
        url = get_itunes_preview(title, artist)
        if not url:
            print(f"    [ERROR] No iTunes preview found -- skipping.")
            return None
        if not download_file(url, raw):
            return None
        print(f"    [INFO] Downloaded {raw.stat().st_size // 1024} KB")

    work_dir  = song_dir / "_work"
    work_dir.mkdir(exist_ok=True)
    stems_dir = run_demucs(raw, work_dir)
    if not stems_dir:
        return None

    mix_stems(stems_dir, ["drums"], stages[0])
    mix_stems(stems_dir, ["drums", "bass"], stages[1])
    mix_stems(stems_dir, ["drums", "bass", "guitar"], stages[2])
    mix_stems(stems_dir, ["drums", "bass", "guitar", "piano"], stages[3])
    mix_stems(stems_dir, ["drums", "bass", "guitar", "piano", "other"], stages[4])
    mix_stems(stems_dir, ["drums", "bass", "guitar", "piano", "other", "vocals"], stages[5])
    mix_stems(stems_dir, ["drums", "bass", "guitar", "piano", "other", "vocals"], stages[6])

    shutil.rmtree(work_dir, ignore_errors=True)

    return _build_entry(song, stages)

def _build_entry(song: dict, stages: list) -> dict:
    return {
        "id":      song["id"],
        "title":   song["title"],
        "artists": song["artists"],
        "stages":  [f"audio/{song['id']}/{s.name}" for s in stages],
    }

def print_file_tree(entries):
    print("\n" + "=" * 60)
    print("GENERATED FILE STRUCTURE")
    print("=" * 60)
    print("dataComp.json")
    print("audio/")
    for i, entry in enumerate(entries):
        is_last_song = (i == len(entries) - 1)
        song_prefix = " └── " if is_last_song else " ├── "
        print(f"{song_prefix}{entry['id']}/")
        stages = entry['stages']
        for j, stage in enumerate(stages):
            is_last_stage = (j == len(stages) - 1)
            if not is_last_song:
                stage_prefix = " │   └── " if is_last_stage else " │   ├── "
            else:
                stage_prefix = "     └── " if is_last_stage else "     ├── "
            filename = stage.split('/')[-1]
            print(f"{stage_prefix}{filename}")
    print("=" * 60)

def main():
    AUDIO_DIR.mkdir(exist_ok=True)
    entries = []

    for i, song in enumerate(SONGS, 1):
        print(f"\n[{i}/{len(SONGS)}] {song['title']} -- {song['artists'][0]}")
        entry = process_song(song)
        if entry:
            entries.append(entry)
        else:
            print(f"    [WARN] '{song['title']}' was skipped.")

    DATA_FILE.write_text(
        json.dumps({"songs": entries}, indent=2, ensure_ascii=False)
    )

    print_file_tree(entries)

    manifest_path = Path("file_manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as mf:
        mf.write("STEMGUESSER AUDIO FILE MANIFEST\n")
        mf.write("=" * 50 + "\n\n")
        for entry in entries:
            mf.write(f"Song: {entry['title']} by {', '.join(entry['artists'])}\n")
            mf.write(f"ID: {entry['id']}\n")
            for i, stage_path in enumerate(entry['stages'], 1):
                abs_path = Path(stage_path).resolve()
                mf.write(f"  Stage {i}: {stage_path}\n")
                mf.write(f"    Full Path: {abs_path}\n")
            mf.write("\n")
    print(f"\n[FILE] Manifest saved to {manifest_path.resolve()}")

    sep = "=" * 52
    print(f"\n{sep}")
    print(f"[OK] {len(entries)}/{len(SONGS)} songs ready.")
    print(f"[FILE] {DATA_FILE}")
    print(f"[DIR] {AUDIO_DIR}/")
    print(f"\nNow push these to GitHub:")
    print(f"  git add dataComp.json audio/ index.html game.js .gitignore")
    print(f"  git commit -m 'Add songs'")
    print(f"  git push")

if __name__ == "__main__":
    main()