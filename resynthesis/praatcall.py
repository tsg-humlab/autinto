import parselmouth

def send_to_praat(script):
    # Praat output different than a file is difficult, so we use a pipe to handle it.
    pipename = str(time.time_ns()) + '.wav'
    os.mkfifo(pipename)

    # We extend the script with a write call to write to this pipe
    script += "Write to WAV file... '.' '" + pipename + "'\n"

    # And to make sure we can read it we add a thread for praat to execute in
    praatexec = threading.Thread(target=parselmouth.praat.run, args=(script,))

    # Then we start reading the file, start praat, and assert everything was read.
    f = os.open(pipename, os.O_NONBLOCK | os.O_RDONLY)
    praatexec.start()
    wavcontent = os.read(f, 1_000_000)
    assert(len(wavcontent) < 1_000_000)
    
    # Wait on Praat and remove pipe
    praatexec.join()
    os.unlink(pipename)

    return wavcontent



