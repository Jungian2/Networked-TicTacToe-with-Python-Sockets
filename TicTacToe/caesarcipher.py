import random


class CaesarCipher:
    shift_num = random.randint(0, 38)

    @staticmethod
    def encrypt(n, plaintext):
        """Encrypt the string and return the ciphertext"""
        key = 'abcdefghijklmnopqrstuvwxyz0123456789[]'
        result = ''

        for l in plaintext:
            try:
                i = (key.index(l) + int(n)) % 38
                result += key[i]
            except ValueError:
                result += l

        return result

    @staticmethod
    def decrypt(n, ciphertext):
        """Decrypt the string and return the ciphertext"""
        result = ''
        key = 'abcdefghijklmnopqrstuvwxyz0123456789[]'

        for l in ciphertext:
            try:
                i = (key.index(l) - int(n)) % 38
                result += key[i]
            except ValueError:
                result += l
        return result


# Allows for the testing of different shift values
if __name__ == "__main__":
    cipher = "hello friend"
    shift = 3
    cip = CaesarCipher()
    encrypted = cip.encrypt(shift, cipher)
    decrypted = cip.decrypt(shift, encrypted)
    print("Original: ", cipher)
    print("Encrypted: ", encrypted)
    print("Decrypted: ", decrypted)
