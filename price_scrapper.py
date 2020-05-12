from bankier_scr import price_extracter, convert_to_number

# dekorator 
def convert_decorator(funkcja):
    def returns_converted(s):
        result_tuple = funkcja(s)
        if result_tuple is None: return None
        return tuple(convert_to_number(n) for n in result_tuple)
    return returns_converted


price_extracter_conv = convert_decorator(price_extracter)   #zapięcie dekoratora
