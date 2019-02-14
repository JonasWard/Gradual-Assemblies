# check dir functions

# if (self.chng_dir == 0):
#     # no change
#     self.swap_u = False
#     self.swap_v = False
# elif (self.chng_dir == 1):
#     # invert u direction
#     self.swap_u = True
#     self.swap_v = False
# elif (self.chng_dir == 2):
#     # invert u direction
#     self.swap_u = False
#     self.swap_v = True
# elif (self.chng_dir == 3):
#     # invert u & v direction
#     self.swap_u = True
#     self.swap_v = True

for value in range(4):

    swap_u = (value % 2 == 1)
    swap_v = (value > 1)

    print("value ", value, " : ", swap_u, ", ", swap_v)

value  0  :  False ,  False
value  1  :  True ,  False
value  2  :  False ,  True
value  3  :  True ,  True
