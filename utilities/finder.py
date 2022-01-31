try:
    import re
    from crypto_solver.Ciphey import mainDecipher
    import base64
    from utilities.utilities import log
except Exception as e:
    raise ImportError("finder.py -> " + str(e))


def find_flag(flag_format,plaintext=None,verbose=False,challenge=None,ciphey_search=False,intensive_ciphey=False):
    if not plaintext:
        log("[!] flag_finder.py wasn't given any input")
        exit(0)
    #elif challenge:
    #	challenge.log("Trying to find flag in: "+str(plaintext)[:20]+("..." if len(plaintext)>20 else ""),verbose=verbose,state=2)
    #else:
    #	log("Trying to find flag in: "+str(plaintext)[:20]+("..." if len(plaintext)>20 else ""),state=2)


    if not flag_format:
        log("Flag format was not given!",state=4)
        exit(0)


    #Change bytes/raw to string if plaintext

    #Flag length and format guessing with previous flag => Store flag
    base_pattern = flag_format+r'{.{2,100}}' #Base pattern to do if no other pattern are found or other pattern is unsucessful
    #If flag format is extensive
    #Try learning => if flag md5 like, check for md5 after, l33t, etc...

    pattern=None
    if "{" in flag_format and '}' in flag_format:
        flag_ext= re.findall(r"{.*}",flag_format)[0][1:-1] if re.findall(r"{.*}", flag_format) else "" #Regex to find extention in "flag{extention}"

        if flag_ext.lower()=="md5":
            pattern = flag_format.split("{")[0]+r'{[a-fA-F\d]{32}}'
        elif flag_ext.lower()=="sha1" or flag_ext.lower()=="sha-1":
            pattern = flag_format.split("{")[0]+r'{[0-9a-f]{40}}'

        base_pattern = flag_format.split("{")[0]+r'{.{2,100}}'    #Base regex pattern
    else:
        base_pattern = flag_format.replace("{","").replace("}","")+r'{.{2,100}}'


    #Regex flags
    pattern_matches=[]
    base_matches=[]
    if pattern:
        pattern_matches+=re.findall(pattern,plaintext)
    base_matches+=re.findall(base_pattern,plaintext)

    #Remove duplicates
    pattern_matches=list(set(pattern_matches))
    base_matches=[x for x in list(set(base_matches)) if x not in pattern_matches]


    #Flags that match flag specific pattern
    if pattern:
        if len(pattern_matches)==1:
            if challenge:
                challenge.flag_log(pattern_matches[0])
                challenge.log("Found this flag that matches your specific pattern: "+pattern_matches[0],verbose=True, state=0)
            else:
                log("Found this flag that matches your specific pattern: "+pattern_matches[0], state=0)
            return True
        elif len(pattern_matches)>1:
            if len(pattern_matches)>100:
                for flag in pattern_matches[:100]:
                    if challenge:
                        challenge.flag_log(flag)
                        challenge.log("Found this flag that matches your specific pattern: "+flag,verbose=True, state=0)
                    else:
                        log("Found this flag that matches your specific pattern: "+flag, state=0)

            else:
                for flag in pattern_matches:
                    if challenge:
                        challenge.flag_log(flag)
                        challenge.log("Found this flag that matches your specific pattern: "+flag,verbose=True, state=0)
                    else:
                        log("Found this flag that matches your specific pattern: "+flag, state=0)

            return None
        if len(base_matches)==1:
            if challenge:
                challenge.flag_log(base_matches[0])
                challenge.log("Found this flag but it doesn't match your pattern: "+base_matches[0],verbose=verbose, state=2)
            else:
                log("Found this flag but it doesn't match your pattern: "+base_matches[0], state=2)
            return True
        elif len(base_matches)>1:
            if len(base_matches)>100:
                for flag in base_matches[:100]:	
                    if challenge:
                        challenge.flag_log(flag)
                        challenge.log("Found this flag but it doesn't match your pattern: "+flag,verbose=verbose, state=2)
                    else:
                        log("Found this flag but it doesn't match your pattern: "+flag, state=2)
            else:
                for flag in base_matches:
                    if challenge:
                        challenge.flag_log(flag)
                        challenge.log("Found this flag but it doesn't match your pattern: "+flag,verbose=verbose, state=2)
                    else:
                        log("Found this flag but it doesn't match your pattern: "+flag, state=2)
            return None
        elif verbose:
            # print("[!] Could not find flag in "+plaintext)
            return False
    else:
        # Flags that only match the flag format
        if len(base_matches)==0 and ciphey_search:
            try:
                # We regrep with ignoring the case
                base_matches+=re.findall(base_pattern,plaintext,re.IGNORECASE)
                # We regrep with the b64 flag format
                b64pattern_matches=[]
                flag_first_part=(flag_format.split("{")[0] +"{").encode()
                base64flag=(base64.b64encode(flag_first_part)).decode() #Encode beginning of flag format in b64

                b64pattern=base64flag[:len(base64flag)-(len(base64flag)%4)]+r'[-A-Za-z0-9+=/]*' 	# pattern with last 4 char complete block and base64 rest
                b64pattern_matches+=re.findall(b64pattern,plaintext,re.IGNORECASE)
                
                for match in b64pattern_matches:
                    base_matches+=re.findall(base_pattern,str(mainDecipher(match,5)))
            except:
                pass
            # We ciphey if b64 and ignore case if it didn't work 
            if len(base_matches)==0 and intensive_ciphey:
                lines=plaintext.split("\n")
                for line in lines:
                    base_matches+=re.findall(base_pattern,str(mainDecipher(line,5)),re.IGNORECASE)
                    #print("base_matches2:",base_matches)
                    #input()
                if len(base_matches)==0:
                    words=[x for x in plaintext.split(" ") if len(x)>7]
                    for word in words:
                        base_matches+=re.findall(base_pattern,str(mainDecipher(word,5)),re.IGNORECASE)
                        #print("base_matches3:",base_matches)
                        #input()
                if len(base_matches)==0:
                    #If we have no match, we still try to decode and log them but not as flags
                    decoded_text=[]
                    for line in lines:
                        decoded_text+=mainDecipher(line,5)
                    for word in words:
                        decoded_text+=mainDecipher(word,5)
                    if len(decoded_text)!=0:
                        challenge.log("##### These have been decoded by ciphey but do not match the flag pattern:",verbose=verbose,state=2)
                        for text in decoded_text:
                            challenge.log(text,verbose=verbose,state=2)



        if len(base_matches)==1:
            
            if challenge:
                challenge.flag_log(base_matches[0])
                challenge.log("Found this flag: "+base_matches[0], verbose=True, state=0)
            else:
                log("Found this flag: "+base_matches[0], state=0)
            return True
        elif len(base_matches)>1:
            if len(base_matches)>100:
                for flag in base_matches[:100]:
                    if challenge:
                        challenge.flag_log(base_matches[0])
                        challenge.log("Found this flag: "+base_matches[0], verbose=True, state=0)
                    else:
                        log("Found this flag: "+base_matches[0], state=0)
            else:
                for flag in base_matches:
                    if challenge:
                        challenge.flag_log(base_matches[0])
                        challenge.log("Found this flag: "+base_matches[0], verbose=True, state=0)
                    else:
                        log("Found this flag: "+base_matches[0], state=0)
            return None
        #elif verbose:
            # print("[!] Could not find flag")
    return False
    