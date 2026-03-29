import array

class StandardPostings:
    """ 
    Class dengan static methods, untuk mengubah representasi postings list
    yang awalnya adalah List of integer, berubah menjadi sequence of bytes.
    Kita menggunakan Library array di Python.

    ASUMSI: postings_list untuk sebuah term MUAT di memori!

    Silakan pelajari:
        https://docs.python.org/3/library/array.html
    """

    @staticmethod
    def encode(postings_list):
        """
        Encode postings_list menjadi stream of bytes

        Parameters
        ----------
        postings_list: List[int]
            List of docIDs (postings)

        Returns
        -------
        bytes
            bytearray yang merepresentasikan urutan integer di postings_list
        """
        # Untuk yang standard, gunakan L untuk unsigned long, karena docID
        # tidak akan negatif. Dan kita asumsikan docID yang paling besar
        # cukup ditampung di representasi 4 byte unsigned.
        return array.array('L', postings_list).tobytes()

    @staticmethod
    def decode(encoded_postings_list):
        """
        Decodes postings_list dari sebuah stream of bytes

        Parameters
        ----------
        encoded_postings_list: bytes
            bytearray merepresentasikan encoded postings list sebagai keluaran
            dari static method encode di atas.

        Returns
        -------
        List[int]
            list of docIDs yang merupakan hasil decoding dari encoded_postings_list
        """
        decoded_postings_list = array.array('L')
        decoded_postings_list.frombytes(encoded_postings_list)
        return decoded_postings_list.tolist()

    @staticmethod
    def encode_tf(tf_list):
        """
        Encode list of term frequencies menjadi stream of bytes

        Parameters
        ----------
        tf_list: List[int]
            List of term frequencies

        Returns
        -------
        bytes
            bytearray yang merepresentasikan nilai raw TF kemunculan term di setiap
            dokumen pada list of postings
        """
        return StandardPostings.encode(tf_list)

    @staticmethod
    def decode_tf(encoded_tf_list):
        """
        Decodes list of term frequencies dari sebuah stream of bytes

        Parameters
        ----------
        encoded_tf_list: bytes
            bytearray merepresentasikan encoded term frequencies list sebagai keluaran
            dari static method encode_tf di atas.

        Returns
        -------
        List[int]
            List of term frequencies yang merupakan hasil decoding dari encoded_tf_list
        """
        return StandardPostings.decode(encoded_tf_list)

class VBEPostings:
    """ 
    Berbeda dengan StandardPostings, dimana untuk suatu postings list,
    yang disimpan di disk adalah sequence of integers asli dari postings
    list tersebut apa adanya.

    Pada VBEPostings, kali ini, yang disimpan adalah gap-nya, kecuali
    posting yang pertama. Barulah setelah itu di-encode dengan Variable-Byte
    Enconding algorithm ke bytestream.

    Contoh:
    postings list [34, 67, 89, 454] akan diubah dulu menjadi gap-based,
    yaitu [34, 33, 22, 365]. Barulah setelah itu di-encode dengan algoritma
    compression Variable-Byte Encoding, dan kemudian diubah ke bytesream.

    ASUMSI: postings_list untuk sebuah term MUAT di memori!

    """

    @staticmethod
    def vb_encode_number(number):
        """
        Encodes a number using Variable-Byte Encoding
        Lihat buku teks kita!
        """
        bytes = []
        while True:
            bytes.insert(0, number % 128) # prepend ke depan
            if number < 128:
                break
            number = number // 128
        bytes[-1] += 128 # bit awal pada byte terakhir diganti 1
        return array.array('B', bytes).tobytes()

    @staticmethod
    def vb_encode(list_of_numbers):
        """ 
        Melakukan encoding (tentunya dengan compression) terhadap
        list of numbers, dengan Variable-Byte Encoding
        """
        bytes = []
        for number in list_of_numbers:
            bytes.append(VBEPostings.vb_encode_number(number))
        return b"".join(bytes)

    @staticmethod
    def encode(postings_list):
        """
        Encode postings_list menjadi stream of bytes (dengan Variable-Byte
        Encoding). JANGAN LUPA diubah dulu ke gap-based list, sebelum
        di-encode dan diubah ke bytearray.

        Parameters
        ----------
        postings_list: List[int]
            List of docIDs (postings)

        Returns
        -------
        bytes
            bytearray yang merepresentasikan urutan integer di postings_list
        """
        gap_postings_list = [postings_list[0]]
        for i in range(1, len(postings_list)):
            gap_postings_list.append(postings_list[i] - postings_list[i-1])
        return VBEPostings.vb_encode(gap_postings_list)

    @staticmethod
    def encode_tf(tf_list):
        """
        Encode list of term frequencies menjadi stream of bytes

        Parameters
        ----------
        tf_list: List[int]
            List of term frequencies

        Returns
        -------
        bytes
            bytearray yang merepresentasikan nilai raw TF kemunculan term di setiap
            dokumen pada list of postings
        """
        return VBEPostings.vb_encode(tf_list)

    @staticmethod
    def vb_decode(encoded_bytestream):
        """
        Decoding sebuah bytestream yang sebelumnya di-encode dengan
        variable-byte encoding.
        """
        n = 0
        numbers = []
        decoded_bytestream = array.array('B')
        decoded_bytestream.frombytes(encoded_bytestream)
        bytestream = decoded_bytestream.tolist()
        for byte in bytestream:
            if byte < 128:
                n = 128 * n + byte
            else:
                n = 128 * n + (byte - 128)
                numbers.append(n)
                n = 0
        return numbers

    @staticmethod
    def decode(encoded_postings_list):
        """
        Decodes postings_list dari sebuah stream of bytes. JANGAN LUPA
        bytestream yang di-decode dari encoded_postings_list masih berupa
        gap-based list.

        Parameters
        ----------
        encoded_postings_list: bytes
            bytearray merepresentasikan encoded postings list sebagai keluaran
            dari static method encode di atas.

        Returns
        -------
        List[int]
            list of docIDs yang merupakan hasil decoding dari encoded_postings_list
        """
        decoded_postings_list = VBEPostings.vb_decode(encoded_postings_list)
        total = decoded_postings_list[0]
        ori_postings_list = [total]
        for i in range(1, len(decoded_postings_list)):
            total += decoded_postings_list[i]
            ori_postings_list.append(total)
        return ori_postings_list

    @staticmethod
    def decode_tf(encoded_tf_list):
        """
        Decodes list of term frequencies dari sebuah stream of bytes

        Parameters
        ----------
        encoded_tf_list: bytes
            bytearray merepresentasikan encoded term frequencies list sebagai keluaran
            dari static method encode_tf di atas.

        Returns
        -------
        List[int]
            List of term frequencies yang merupakan hasil decoding dari encoded_tf_list
        """
        return VBEPostings.vb_decode(encoded_tf_list)

class EliasGammaPostings:
    """
    Bit-level compression menggunakan Elias-Gamma coding.

    Untuk postings list, kita encode gap-based list (seperti pada VBEPostings).
    Karena Elias-Gamma hanya mendukung integer >= 1, setiap angka di-offset +1
    saat encoding, lalu -1 saat decoding.
    """

    @staticmethod
    def _gamma_encode_number(number):
        """
        Elias-Gamma encode untuk integer >= 1.
        Hasilnya berupa list of bits (0/1).
        """
        if number <= 0:
            raise ValueError("Elias-Gamma hanya mendukung integer >= 1")

        # binary tanpa leading '0b'
        binary = bin(number)[2:]
        prefix_zeros = len(binary) - 1
        bits = ([0] * prefix_zeros) + [1] + [int(b) for b in binary[1:]]
        return bits

    @staticmethod
    def _gamma_encode(list_of_numbers):
        """
        Encode list of numbers menjadi bytestream menggunakan Elias-Gamma.
        """
        bits = []
        for number in list_of_numbers:
            bits.extend(EliasGammaPostings._gamma_encode_number(number))
        return EliasGammaPostings._bits_to_bytes(bits)

    @staticmethod
    def _gamma_decode(encoded_bytestream):
        """
        Decode bytestream Elias-Gamma menjadi list of numbers.
        """
        bits = EliasGammaPostings._bytes_to_bits(encoded_bytestream)
        numbers = []
        i = 0
        n_bits = len(bits)
        while i < n_bits:
            # hitung unary prefix (jumlah 0 sebelum 1)
            zeros = 0
            while i < n_bits and bits[i] == 0:
                zeros += 1
                i += 1
            if i >= n_bits:
                break  # padding zeros di akhir
            # bits[i] == 1
            i += 1
            # baca sisa (zeros) bit untuk binary suffix
            if i + zeros > n_bits:
                break  # tidak lengkap (padding)
            suffix_bits = bits[i:i+zeros]
            i += zeros
            binary = '1' + ''.join(str(b) for b in suffix_bits)
            numbers.append(int(binary, 2))
        return numbers

    @staticmethod
    def _bits_to_bytes(bits):
        """
        Ubah list bit (0/1) menjadi bytestream.
        Padding dengan 0 sampai kelipatan 8.
        """
        if not bits:
            return b""
        pad_len = (8 - (len(bits) % 8)) % 8
        bits += [0] * pad_len
        bytes_out = array.array('B')
        for i in range(0, len(bits), 8):
            byte_val = 0
            for bit in bits[i:i+8]:
                byte_val = (byte_val << 1) | bit
            bytes_out.append(byte_val)
        return bytes_out.tobytes()

    @staticmethod
    def _bytes_to_bits(encoded_bytestream):
        """
        Ubah bytestream menjadi list bit (0/1).
        """
        if not encoded_bytestream:
            return []
        bytes_arr = array.array('B')
        bytes_arr.frombytes(encoded_bytestream)
        bits = []
        for byte in bytes_arr:
            for shift in range(7, -1, -1):
                bits.append((byte >> shift) & 1)
        return bits

    @staticmethod
    def encode(postings_list):
        """
        Encode postings_list menjadi stream of bytes (Elias-Gamma).
        Postings diubah ke gap-based list, lalu di-offset +1.
        """
        gap_postings_list = [postings_list[0]]
        for i in range(1, len(postings_list)):
            gap_postings_list.append(postings_list[i] - postings_list[i-1])
        gap_postings_list = [g + 1 for g in gap_postings_list]
        return EliasGammaPostings._gamma_encode(gap_postings_list)

    @staticmethod
    def encode_tf(tf_list):
        """
        Encode list of term frequencies menjadi stream of bytes (Elias-Gamma).
        TF di-offset +1 agar >= 1.
        """
        tf_list = [tf + 1 for tf in tf_list]
        return EliasGammaPostings._gamma_encode(tf_list)

    @staticmethod
    def decode(encoded_postings_list):
        """
        Decode postings_list dari bytestream Elias-Gamma.
        Hasil decoding masih gap-based list dan perlu di-offset -1.
        """
        decoded_gaps_plus1 = EliasGammaPostings._gamma_decode(encoded_postings_list)
        if not decoded_gaps_plus1:
            return []
        decoded_gaps = [g - 1 for g in decoded_gaps_plus1]
        total = decoded_gaps[0]
        ori_postings_list = [total]
        for i in range(1, len(decoded_gaps)):
            total += decoded_gaps[i]
            ori_postings_list.append(total)
        return ori_postings_list

    @staticmethod
    def decode_tf(encoded_tf_list):
        """
        Decode list of term frequencies dari bytestream Elias-Gamma.
        """
        decoded_tf_plus1 = EliasGammaPostings._gamma_decode(encoded_tf_list)
        return [tf - 1 for tf in decoded_tf_plus1]

if __name__ == '__main__':
    
    postings_list = [34, 67, 89, 454, 2345738]
    tf_list = [12, 10, 3, 4, 1]
    for Postings in [StandardPostings, VBEPostings, EliasGammaPostings]:
        print(Postings.__name__)
        encoded_postings_list = Postings.encode(postings_list)
        encoded_tf_list = Postings.encode_tf(tf_list)
        print("byte hasil encode postings: ", encoded_postings_list)
        print("ukuran encoded postings   : ", len(encoded_postings_list), "bytes")
        print("byte hasil encode TF list : ", encoded_tf_list)
        print("ukuran encoded postings   : ", len(encoded_tf_list), "bytes")
        
        decoded_posting_list = Postings.decode(encoded_postings_list)
        decoded_tf_list = Postings.decode_tf(encoded_tf_list)
        print("hasil decoding (postings): ", decoded_posting_list)
        print("hasil decoding (TF list) : ", decoded_tf_list)
        assert decoded_posting_list == postings_list, "hasil decoding tidak sama dengan postings original"
        assert decoded_tf_list == tf_list, "hasil decoding tidak sama dengan postings original"
        print()
