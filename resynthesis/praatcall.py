import parselmouth

def send_to_praat(script):
    pipename = str(time.time_ns()) + '.wav'
    os.mkfifo(pipename)

    script += "Write to WAV file... '.' '" + pipename + "'\n"
    praatexec = threading.Thread(target=parselmouth.praat.run, args=(script,))

    f = os.open(pipename, os.O_NONBLOCK | os.O_RDONLY)
    praatexec.start()
    wavcontent = os.read(f, 1_000_000)
    assert(len(wavcontent) < 1_000_000)
    
    praatexec.join()
    os.unlink(pipename)

    return wavcontent



