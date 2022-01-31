try:
    from utilities.utilities import timeout
    from ciphey import decrypt
    from ciphey.iface import Config
except Exception as e:
    raise ImportError("Ciphey.py -> " + str(e))

# Register an handler for the timeout
#def handler(signum, frame):
#    print("Not able to crack")
#    raise Exception("TimeOut")
 

# This function *may* run for an indetermined time...
def decipher(text):#la fonction Ciphey
    res = decrypt(
        Config().library_default().complete_config(),
        text,)
    return res
         
         

# Register the signal function handler
#signal.signal(signal.SIGALRM, handler)

# Define a timeout for your function
def mainDecipher(text,sec=2):

    try:
        with timeout(sec):
            result = decipher(text)
            if result!="Failed to crack":
                return result
            else:
                return False
    except Exception: 
        print("Ciphey timeout")
        return False

#mainDecipher("Uryyb zl anzr vf orr naq V yvxr qbt naq nccyr naq gerr",5)

#signal.alarm(0)
                 
