import pstats
p = pstats.Stats('profile.prof')
p.strip_dirs().sort_stats('cumtime').print_stats(50)