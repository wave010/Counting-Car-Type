string_ex = "250,180,640,180"
list_of_integers = string_ex.split(",")
list_of_integers = [int(x) for x in list_of_integers]
print(list_of_integers)