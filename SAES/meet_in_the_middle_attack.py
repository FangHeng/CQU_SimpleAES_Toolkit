# -*- coding: utf-8 -*-
# @Time    : 2023/10/20 15:51
# @Author  : Fang Heng
# @File    : meet_in_the_middle_attack.py
# @Software: PyCharm 
# @Comment :

# 加载实现的加密算法类
from SAES import SAES

def meet_in_the_middle_attack(pairs):
    """
    使用中间相遇攻击找到可能的key1和key2对。
    输入：pairs - 明密文对的列表，如[(plaintext1, ciphertext1), (plaintext2, ciphertext2), ...]
    输出：所有可能的(key1, key2)对的列表
    """
    SAES_instance = SAES("0" * 16)  # 创建一个默认密钥的SAES实例
    possible_keys_set = None  # 存储所有明密文对的交集

    for plaintext, ciphertext in pairs:
        encrypt_dict = {}
        current_possible_keys = set()

        # Step 1: 从明文开始加密，直到中间值
        for key1 in range(2**16):  # 遍历所有可能的16位key1
            SAES_instance.key = format(key1, '016b')
            intermediate_ciphertext = SAES_instance._single_encrypt(plaintext)
            encrypt_dict[intermediate_ciphertext] = SAES_instance.key

        # Step 2: 从密文开始解密，直到中间值
        for key2 in range(2**16):  # 遍历所有可能的16位key2
            SAES_instance.key = format(key2, '016b')
            intermediate_plaintext = SAES_instance._single_decrypt(ciphertext)
            if intermediate_plaintext in encrypt_dict:  # 查找是否有匹配的中间值
                current_possible_keys.add((encrypt_dict[intermediate_plaintext], SAES_instance.key))

        if possible_keys_set is None:
            possible_keys_set = current_possible_keys
        else:
            possible_keys_set &= current_possible_keys

    return list(possible_keys_set)


if __name__=='__main__':
    # 1. 只使用一对明密文对
    print("1. 只使用一对明密文对")
    pairs1 = [("1101011100101100", "0110110100111010")]
    potential_keys = meet_in_the_middle_attack(pairs1)

    print(f"Number of potential key pairs: {len(potential_keys)}")

    print("--------------------")

    # 2. 使用两对明密文对
    print("2. 使用两对明密文对")
    pairs2 = [
        ("1101011100101100", "0110110100111010"),
        ("1111111100000000", "0111011011110111")
    ]
    potential_keys = meet_in_the_middle_attack(pairs2)
    print(f"Number of potential key pairs: {len(potential_keys)}")
    print(f"Potential key pairs: {potential_keys}")