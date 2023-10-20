from django.shortcuts import render,HttpResponse
from SAES.SAES import SAES
from django.http import JsonResponse

def start(request):
    return render(request,"index.html")

def index(request):
    return render(request,"index.html")


def plaintext_sent(request):
    if request.method == 'POST':
        key_input = request.POST['key']
        plaintext_input = request.POST['plaintext']
        type = request.POST['type']
        if type == "ASCII":
            saes = SAES(key=key_input)
            out = ""

            # 转换输入为二进制
            binary_input = ''.join([bin(ord(char)).replace("0b", "").zfill(8) for char in plaintext_input])

            # 检查字符数并进行填充
            if len(plaintext_input) % 2 == 1:  # 奇数字符，添加00000001
                binary_input += '00000001'
            else:  # 偶数字符，添加00000010 00000010
                binary_input += '00000010' + '00000010'

            for i in range(0, len(binary_input), 16):
                bin_block = binary_input[i:i + 16]
                out_hex = hex(int(saes.encrypt(bin_block), 2))[2:].zfill(4)  # 加密并转换为16进制
                out += out_hex

            data = {
                "ciphertext": out
            }
            return JsonResponse(data)

        elif type == "Bit":
            saes = SAES(key=key_input)
            out_bin = saes.encrypt(plaintext_input)
            out_hex = hex(int(out_bin, 2))[2:].zfill(4)
            data = {
                "ciphertext": out_bin
            }
            return JsonResponse(data)


def ciphertext_sent(request):
    #
    # 用户输入的文本就记作：plaintext
    if request.method == 'POST':
        key_input = request.POST['key']
        ciphertext_input = request.POST['plaintext']
        type = request.POST['type']

        # 实例化SAES对象
        saes = SAES(key=key_input)

        if type == "ASCII":
            out = ""

            # 每4个字符（16位）解密一次
            for i in range(0, len(ciphertext_input), 4):
                hex_block = ciphertext_input[i:i + 4]
                bin_block = bin(int(hex_block, 16)).replace("0b", "").zfill(16)
                out_bin = saes.decrypt(bin_block)

                # 从二进制块中检索原始字符
                out_chr1 = chr(int(out_bin[:8], 2))
                out_chr2 = chr(int(out_bin[8:], 2))

                # 检查填充字符并按需要删除它们
                if out_bin[8:] == '00000001':
                    out += out_chr1
                elif out_bin[:8] == '00000010' and out_bin[8:] == '00000010':
                    continue
                else:
                    out += out_chr1 + out_chr2

            data = {
                "ciphertext": out
            }
            return JsonResponse(data)

        elif type == "Bit":
            bin_input = bin(int(ciphertext_input,2)).replace("0b", "").zfill(16)
            out_bin = saes.decrypt(bin_input)
            data = {
                "ciphertext": out_bin
            }
            return JsonResponse(data)

