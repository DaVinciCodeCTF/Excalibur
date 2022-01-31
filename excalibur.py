try:
    import os
    from pathlib import Path, PurePath
    import sys
    sys.path.insert(1, str(Path(os.path.realpath(__file__)).parents[0].joinpath("web_solver")))
    import argparse
    from utilities.utilities import log
    import utilities.ctfd_scraper as ctfd_scraper
    import web_solver.util as web_util
    import web_solver.web as web_solver
    from multiprocessing import Pool, cpu_count
    import crypto_solver.cryptodispatcher as crypto
    import stega_solver.stega as stega
    import forensics_solver.forensics as forensics
    import utilities.finder as finder
except Exception as e:
    print("Import error : excalibur.py -> " + str(e))
    # exit(0)


def solve_challenge(challenge, args):
    try:
        if not challenge.solved:
            log("Solving " + challenge.name, 2)
            if challenge.type == "standard" or challenge.type == "dynamic":
                if 'web' in challenge.category:
                    url = web_util.extract_url(challenge.desc)
                    if url is None:
                        log("[!] URL not found!", 4)
                    elif not web_util.check_if_up(url):
                        log("[!] URL not responding!", 4)
                    else:
                        web_solver.Web(url, args.flag_format, args.verbose, challenge, args.threads)
                elif 'crypt' in challenge.category:
                    crypto.solve(challenge, args)
                elif 'steg' in challenge.category:
                    stega.solve(challenge, args)
                    #forensics.solve(challenge, args)
                elif 'forens' in challenge.category:
                    forensics.solve(challenge, args)
                    #stega.solve(challenge, args)
                else:
                    challenge.log(
                        "This challenge is not a standard challenge, it's a " + challenge.type +
                        " challenge, you need to do this on your own uwu", 3)
    except Exception as exc:
        log(str(exc), 4)
    challenge.solved = True


def main():
    parser = argparse.ArgumentParser(description='Main function for the solver')

    parser.add_argument('--chall', action='store_true', default=False,
                        help='Excalibur will try to solve a specific given challenge from an input, file or link')
    parser.add_argument('--ctf', type=str,
                        help='Excalibur will try to solve a full CTF deployed with CTFd')

    parser.add_argument('--login', type=str,
                        help='Login username for the CTF')
    parser.add_argument('--password', type=str,
                        help='Login password for the CTF')

    parser.add_argument('-p', '--path', type=str,
                        help='File to be analysed')
    parser.add_argument('-u', '--url', type=str,
                        help='URL to be analysed')
    parser.add_argument('-t', '--text', type=str,
                        help='Plaintext to be analysed')

    parser.add_argument('-c', '--crypto', action='store_true', default=False,
                        help='Flag to specify that the given input is for a Cryptography challenge')
    parser.add_argument('-f', '--forensics', action='store_true', default=False,
                        help='Flag to specify that the given input is for a Forensics challenge')
    parser.add_argument('-s', '--stega', action='store_true', default=False,
                        help='Flag to specify that the given input is for a Steganography challenge')
    parser.add_argument('-w', '--web', action='store_true', default=False,
                        help='Flag to specify that the given input is for a Web challenge')

    parser.add_argument('--flag', type=str,
                        help='Flag format of the CTF', dest="flag_format")

    parser.add_argument('-i', '--input', action='store_true', default=False,
                        help='Automatically chooses default options to avoid input')
    parser.add_argument('-o', '--output', type=str,
                        help='Specify path to an output file (only for challenge)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False, help='Increase verbosity')

    parser.add_argument('--cores', type=int,
                        default=1, help='Number of core')

    # Web arguments

    parser.add_argument('--threads', type=int,
                        default=1, help='Number of threads')

    args = parser.parse_args()






    # Check for valid path for input and ouput
    if args.chall:
        if not args.path and not args.url and not args.text:
            log("[!] You haven't specified any input", 4)
            exit(0)
        if args.path:
            if not os.path.exists(args.path):
                log("[!] The file you have specified doesn't exists", 4)
                exit(0)
            else:
                args.path = Path(args.path)

        if not args.crypto and not args.forensics and not args.stega and not args.web:
            if not args.input:
                log("You haven't chosen any category, are you okay with the scan running through all? [Y/n] ", 3)
                if input() == "n":
                    pass
                else:
                    args.crypto = args.forensics = args.stega = True
            else:
                args.crypto = args.forensics = args.stega = True 
  

        if args.output:
            outfile = PurePath.joinpath(Path.cwd(), args.output)
            while os.path.exists(outfile):
                import random
                outfile = PurePath.joinpath(
                    Path.cwd(), outfile.stem + str(random.randint(0, 9999)))
            args.outfile = outfile

        challenge = ctfd_scraper.Challenge(text=args.text,file=args.path)

        if args.text:
            finder.find_flag(verbose=args.verbose,flag_format=args.flag_format, plaintext=args.text, challenge=challenge)

        

        
        elif args.path:
            

            try:
                with open(args.path) as file:
                    finder.find_flag(verbose=args.verbose,flag_format=args.flag_format, plaintext=file.read(), challenge=challenge)
            except:
                try:
                    with open(args.path) as file:
                        finder.find_flag(verbose=args.verbose,flag_format=args.flag_format, plaintext=file.read(encoding='latin-1'), challenge=challenge)
                except:
                    log("Couldn't find correct codecs to read file",state=4)

            if args.forensics:
                forensics.solve(challenge, args)

            if args.stega:
                stega.solve(challenge, args)

            if args.crypto:
                crypto.solve(challenge, args)

        elif args.web:
            if not args.url:
                log("A URL is mandatory, please use -u or --url", 4)
                exit(0)

            url = web_util.extract_url(args.url)
            if url is None:
                log("Bad format for URL", 4)
                exit(0)
            elif not web_util.check_if_up(url):
                log("[!] URL not responding!", 4)
                exit(0)
            web_solver.Web(args.url, args.flag_format, args.verbose, challenge, args.threads)


    



    elif args.ctf:
        if args.flag_format:
            ctf = ctfd_scraper.CTF(args)
            if args.cores > 1:
                with Pool(args.cores) as pool:
                    pool.starmap(solve_challenge, [(chall, args) for chall in ctf.challenges])
                    pool.close()
                    pool.join()
            else:
                for challenge in ctf.challenges:
                    solve_challenge(challenge, args)
            log("All challenges went through the solver!", 0)
        # Check if all challenges are solved
        else:
            log("You need a flag wraper for the ctf option to work! Please use "
                " --flag", 4)
            exit(0)


if __name__ == '__main__':
    main()
