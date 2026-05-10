import argparse
# 将命令行传入的字符串参数，按照你定义的规则进行解析、类型转换和校验。
def main():
    parser = argparse.ArgumentParser(description='一个简单的示例程序')

    parser.add_argument('input', help='输入文件路径') # 位置参数，必须传，否则直接报错退出。类型为 str。
    parser.add_argument('--output', required=False, default='output.txt', help='输出文件路径') # 可选参数。没传时默认为 'output.txt'，传了则覆盖。类型为 str。
    #
    parser.add_argument('--verbose', action='store_true', help='是否打印详细信息')# 布尔开关。命令行出现 --verbose 时为 True，否则为 False。
    parser.add_argument('--times', type=int, default=1, help='重复处理次数') # 自动类型转换。type=int 会让 argparse 自动把字符串转成整数。默认 1。

    args = parser.parse_args()
    print('11111', args)
    # print(args.input)
    if args.verbose:
        print(f"正在处理 {args.input} -> {args.output}，重复 {args.times} 次")

    for i in range(args.times):
        print(f"处理中... {i+1}/{args.times}")

if __name__ == '__main__':
    main()
    # a = not True
    # print(a)
