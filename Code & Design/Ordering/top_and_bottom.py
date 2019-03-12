u_div = 10
v_div = 9

invert = True
even_swap = int(invert)

for u in range(v_div):
    print "\n"
    for v in range(u_div):
        print (u + v + even_swap) % 2, " ",


for u_div in range (3, 5, 1):
    for v_div in range (4, 6, 1):

        bot_val = 0
        top_val = int( (v_div - v_div % 2) / 2 )

        print " \n u_div : ", u_div, " - v_div : ", v_div

        for u in range(v_div):
            print "\n"
            for v in range(u_div):
                print (u + v + even_swap) % 2, " ",

        print " \n"

        print "top row:"

        for i in range(u_div):
            if not((i + even_swap) % 2 == 0):
                print bot_val, (i + even_swap) % 2 * i, " ",

        print " \n"

        print "bottom row:"

        for i in range(u_div):
            if not(((i + v_div - 1 + even_swap) % 2) % 2 == 0):
                print top_val, (i + v_div - 1 + even_swap) % 2 * i, " ",
