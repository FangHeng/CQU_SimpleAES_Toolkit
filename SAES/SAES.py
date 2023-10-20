# -*- coding: utf-8 -*-
# @Time    : 2023/10/20 11:30
# @Author  : Fang Heng
# @File    : SAES.py
# @Software: PyCharm 
# @Comment :

class SAES:
    '''
    S-AES加密类
    '''

    def __init__(self, key,
                 S_BOX=None,
                 S_BOX_INV=None,
                 RCON=None,
                 MixMatrix=None,
                 MixMatrix_INV=None
                 ):
        """ 初始化加密类以及对应的密钥和各种转换盒 """
        # 默认的转换盒
        self.S_BOX = S_BOX if S_BOX else {
            "00": {"00": "1001", "01": "0100", "10": "1010", "11": "1011"},
            "01": {"00": "1101", "01": "0001", "10": "1000", "11": "0101"},
            "10": {"00": "0110", "01": "0010", "10": "0000", "11": "0011"},
            "11": {"00": "1100", "01": "1110", "10": "1111", "11": "0111"},
        }
        self.S_BOX_INV = S_BOX_INV if S_BOX_INV else {
            "00": {"00": "1010", "01": "0101", "10": "1001", "11": "1011"},
            "01": {"00": "0001", "01": "0111", "10": "1000", "11": "1111"},
            "10": {"00": "0110", "01": "0000", "10": "0010", "11": "0011"},
            "11": {"00": "1100", "01": "0100", "10": "1101", "11": "1110"},
        }
        self.RCON = RCON if RCON else ["10000000", "00110000"]
        self.MixMatrix = MixMatrix if MixMatrix else [[1, 4], [4, 1]]
        self.MixMatrix_INV = MixMatrix_INV if MixMatrix_INV else [[9, 2], [2, 9]]

        # 初始化密钥
        self.key = key

    def key_expansion(self):
        """ 密钥扩展算法 """

        def rot_nib(text):
            return text[4:] + text[:4]

        def sub_nib(text):
            left_nibble = text[:4]
            right_nibble = text[4:]
            left_sub = self.S_BOX[left_nibble[:2]][left_nibble[2:]]
            right_sub = self.S_BOX[right_nibble[:2]][right_nibble[2:]]
            return left_sub + right_sub

        w0 = self.key[:8]
        w1 = self.key[8:]
        temp = ''.join([str(int(a) ^ int(b)) for a, b in zip(self.RCON[0], sub_nib(rot_nib(w1)))])
        w2 = ''.join([str(int(a) ^ int(b)) for a, b in zip(w0, temp)])
        w3 = ''.join([str(int(a) ^ int(b)) for a, b in zip(w1, w2)])
        temp = ''.join([str(int(a) ^ int(b)) for a, b in zip(self.RCON[1], sub_nib(rot_nib(w3)))])
        w4 = ''.join([str(int(a) ^ int(b)) for a, b in zip(w2, temp)])
        w5 = ''.join([str(int(a) ^ int(b)) for a, b in zip(w3, w4)])
        return [w0 + w1, w2 + w3, w4 + w5]

    @staticmethod
    def round_key_addition(text, key):
        """ 轮密钥加 """
        return bin(int(text, 2) ^ int(key, 2))[2:].zfill(16)

    def sub_byte(self, text, use_inverse=False):
        """ 字节替代算法 """
        sbox = self.S_BOX_INV if use_inverse else self.S_BOX

        def lookup(sbox, nibble):
            row, col = nibble[:2], nibble[2:]
            return sbox[row][col]

        nibbles = [text[i:i + 4] for i in range(0, len(text), 4)]
        return ''.join(lookup(self.S_BOX, nibble) for nibble in nibbles)

    @staticmethod
    def row_shift(text):
        """ 行位移算法 """
        return text[0:4] + text[12:] + text[8:12] + text[4:8]

    @staticmethod
    def gf_add(a, b):
        """ GF(2^4)域内的加法 """
        if isinstance(a, str):
            a = int(a, 2)
        if isinstance(b, str):
            b = int(b, 2)
        return a ^ b

    @staticmethod
    def gf_mul(a, b):
        """ GF(2^4)域内的乘法 """
        if isinstance(a, str):
            a = int(a, 2)
        if isinstance(b, str):
            b = int(b, 2)
        result = 0
        while b:
            if b & 1:
                result ^= a
            a <<= 1
            b >>= 1
        modulus = 0b10011
        while result >= 0b10000:
            highest_bit_pos = len(bin(result)) - 3
            shift = highest_bit_pos - 4
            result ^= (modulus << shift)
        return result

    @staticmethod
    def mix_column(column, matrix=None):
        """ 列混淆算法 """
        result = [0, 0]
        for i in range(2):
            for j in range(2):
                result[i] = SAES.gf_add(result[i], SAES.gf_mul(matrix[i][j], column[j]))
        return result

    @staticmethod
    def mix_columns(input_string, matrix=None):
        """ 对整个块进行列混淆 """
        matrix_input = [[input_string[i:i + 4] for i in range(0, 8, 4)],
                        [input_string[i + 8:i + 12] for i in range(0, 8, 4)]]
        mixed_column1 = SAES.mix_column(matrix_input[0], matrix)
        mixed_column2 = SAES.mix_column(matrix_input[1], matrix)
        output_string1 = ''.join(format(num, '04b') for num in mixed_column1)
        output_string2 = ''.join(format(num, '04b') for num in mixed_column2)
        return output_string1 + output_string2

    def encrypt(self, plaintext):
        """加密函数，输入明文，输出密文"""

        # 密钥扩展
        keys = self.key_expansion()

        # 初始轮密钥加密
        initial_text = self.round_key_addition(plaintext, keys[0])

        # 第一轮操作
        after_sub_byte1 = self.sub_byte(initial_text)
        after_row_shift1 = self.row_shift(after_sub_byte1)
        after_mix_columns1 = self.mix_columns(after_row_shift1, self.MixMatrix)
        after_key_addition1 = self.round_key_addition(after_mix_columns1, keys[1])

        # 第二轮操作
        after_sub_byte2 = self.sub_byte(after_key_addition1)
        after_row_shift2 = self.row_shift(after_sub_byte2)
        ciphertext = self.round_key_addition(after_row_shift2, keys[2])

        return ciphertext

    def decrypt(self, ciphertext):
        """解密函数，输入密文，输出明文"""

        # 密钥扩展
        keys = self.key_expansion()

        # 初始轮密钥解密
        initial_text = self.round_key_addition(ciphertext, keys[2])

        # 第一轮逆操作
        after_inv_row_shift1 = self.row_shift(initial_text)
        after_inv_sub_byte1 = self.sub_byte(after_inv_row_shift1, use_inverse=True)
        after_inv_key_addition1 = self.round_key_addition(after_inv_sub_byte1, keys[1])

        # 第二轮逆操作
        after_inv_mix_columns1 = self.mix_columns(after_inv_key_addition1, self.MixMatrix_INV)
        after_inv_row_shift2 = self.row_shift(after_inv_mix_columns1)
        after_inv_sub_byte2 = self.sub_byte(after_inv_row_shift2, use_inverse=True)
        plaintext = self.round_key_addition(after_inv_sub_byte2, keys[0])

        return plaintext


if __name__ == '__main__':
    key = '0010110101010101'
    saes = SAES(key=key)

    plaintext = '0110101110100011'
    print(f'本次SAES加密明文为：{plaintext}')
    ciphertext = saes.encrypt(plaintext)
    print(f'通过SAES加密后的密文为：{ciphertext}')
    saes.decrypt(ciphertext)
    print(f'通过SAES解密后的明文为：{plaintext}')
