from SAES import SAES

#plaintext是str类型，key是str类型，iv是str类型
def cbc_encrypt(plaintext, key, iv):
    saes = SAES(key=key)
    previous_cipherblock = iv
    ciphertext = ""

    # 转换输入为二进制
    binary_input = ''.join([bin(ord(char)).replace("0b", "").zfill(8) for char in plaintext])

    # 检查字符数并进行填充
    if len(plaintext) % 2 == 1:  # 奇数字符，添加00000001
        binary_input += '00000001'
    else:  # 偶数字符，添加00000010 00000010
        binary_input += '00000010' + '00000010'

    # 使用CBC模式进行加密
    for i in range(0, len(binary_input), 16):
        block = binary_input[i:i + 16]

        # 明文块与前一个密文块异或
        xor_block = ''.join([str(int(a) ^ int(b)) for a, b in zip(block, previous_cipherblock)])

        cipherblock = saes.encrypt(xor_block)
        ciphertext += cipherblock

        previous_cipherblock = cipherblock

    # 将结果转换为十六进制字符串
    hex_ciphertext = hex(int(ciphertext, 2))[2:].zfill(len(ciphertext) // 4)

    return hex_ciphertext


def cbc_decrypt(ciphertext, key, iv):
    saes = SAES(key=key)
    previous_cipherblock = iv
    binary_output = ""

    # 从十六进制字符串转换为二进制
    binary_input = bin(int(ciphertext, 16))[2:].zfill(len(ciphertext) * 4)

    # 使用CBC模式进行解密
    for i in range(0, len(binary_input), 16):
        block = binary_input[i:i + 16]

        decrypted_block = saes.decrypt(block)

        # 解密块与前一个密文块异或
        xor_block = ''.join([str(int(a) ^ int(b)) for a, b in zip(decrypted_block, previous_cipherblock)])
        binary_output += xor_block

        previous_cipherblock = block

    # 移除填充
    if binary_output[-8:] == '00000001':
        binary_output = binary_output[:-8]
    elif binary_output[-16:] == '00000010' + '00000010':
        binary_output = binary_output[:-16]

    # 将二进制转换回ASCII
    ascii_output = ''.join([chr(int(binary_output[i:i + 8], 2)) for i in range(0, len(binary_output), 8)])

    return ascii_output


if __name__ == "__main__":
    plaintext = "Hello World!"
    key = "0101001000000001"
    iv = "1111001110001011"
    ciphertext = cbc_encrypt(plaintext, key, iv)
    print(f'密文是:{ciphertext}')
    decrypted_text = cbc_decrypt(ciphertext, key, iv)
    print(f'解密后的明文是:{decrypted_text}')
    assert plaintext == decrypted_text
