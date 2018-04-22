import pstats
p = pstats.Stats('profile.prof')
p.strip_dirs().sort_stats('tottime').print_stats(20)