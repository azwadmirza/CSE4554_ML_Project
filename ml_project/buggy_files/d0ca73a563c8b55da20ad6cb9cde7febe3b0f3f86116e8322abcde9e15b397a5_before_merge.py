    def _shred_file_custom(self, tmp_path):
        """"Destroy a file, when shred (core-utils) is not available
        
        Unix `shred' destroys files "so that they can be recovered only with great difficulty with 
        specialised hardware, if at all". It is based on the method from the paper 
        "Secure Deletion of Data from Magnetic and Solid-State Memory", 
        Proceedings of the Sixth USENIX Security Symposium (San Jose, California, July 22-25, 1996).
        
        We do not go to that length to re-implement shred in Python; instead, overwriting with a block
        of random data should suffice. 
        
        See https://github.com/ansible/ansible/pull/13700 .
        """
        
        file_len = os.path.getsize(tmp_path)
        max_chunk_len = min(1024*1024*2, file_len)
        
        passes = 3
        with open(tmp_path,  "wb") as fh:
            for _ in range(passes):
                fh.seek(0,  0)
                # get a random chunk of data, each pass with other length
                chunk_len = random.randint(max_chunk_len/2, max_chunk_len)
                data = os.urandom(chunk_len)
                
                for _ in range(0, file_len // chunk_len):
                    fh.write(data)
                fh.write(data[:file_len % chunk_len])
                
                assert(fh.tell() == file_len) # FIXME remove this assert once we have unittests to check its accuracy
                os.fsync(fh)