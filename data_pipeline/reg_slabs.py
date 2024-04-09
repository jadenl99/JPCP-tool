import argparse
from registration.registration import SlabRegistration
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-b', 
                        metavar='<beginning MM>',
                        type=str,
                        required=True,
                        help='begining MM of the segment')
    
    parser.add_argument('-e',
                        metavar='<ending MM>',
                        type=str,
                        required=True,
                        help='ending MM of the segment')
    
    parser.add_argument('-i', 
                        metavar='<interstate>',
                        type=str,
                        required=True,
                        help='Interstate of data (eg. I16WB)')
    

    begin_MM, end_MM, interstate = list(vars(parser.parse_args()).values())
    begin_MM = int(begin_MM)
    end_MM = int(end_MM)

    if begin_MM < 0 or end_MM < 0:
        raise ValueError("MM cannot be negative")

    
    if ('EB' not in interstate 
        and 'WB' not in interstate 
        and 'NB' not in interstate 
        and 'SB' not in interstate):
        raise ValueError("Please specify direction of interstate highway \
                         (eg. I16WB)")

    
    SlabRegistration(begin_MM, end_MM, interstate)