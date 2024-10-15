import sys
import os
from urllib.parse import urlparse
import csv

def split_file(input_file, max_lines):
    file_counter = 1
    line_counter = 0
    output_file = open(f"output_{file_counter}.txt", "w", encoding='utf-8')

    with open(input_file, "r", encoding='utf-8') as f:
        for line in f:
            if line_counter >= max_lines:
                output_file.close()
                file_counter += 1
                output_file = open(f"output_{file_counter}.txt", "w", encoding='utf-8')
                line_counter = 0

            output_file.write(line)
            line_counter += 1

    output_file.close()

def extract_domains(input_file, output_file):
    domains = set()
    with open(input_file, "r", encoding='utf-8') as f_in:
        for line in f_in:
            line = line.strip()
            if line:
                parsed_url = urlparse(line)
                domain = parsed_url.netloc or parsed_url.path
                if domain:
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    domains.add(domain)
    with open(output_file, "w", encoding='utf-8') as f_out:
        for domain in sorted(domains):
            f_out.write(domain + '\n')

def compare_files(domains_file, links_file, output_file, include_numbers=False, export_csv=False):
    
    domains = {}
    with open(domains_file, 'r', encoding='utf-8') as f_domains:
        for line in f_domains:
            line = line.strip()
            if line:
                parts = line.split('\t')
                if len(parts) >= 2 and include_numbers:
                    domain = parts[0]
                    number = parts[1]
                else:
                    domain = parts[0]
                    number = '' if include_numbers else None
                if domain.startswith('www.'):
                    domain = domain[4:]
                domains[domain] = number

    matched_lines = []

    with open(links_file, 'r', encoding='utf-8') as f_links:
        for line in f_links:
            original_line = line.strip()
            if original_line:
                parsed_url = urlparse(original_line)
                link_domain = parsed_url.netloc or parsed_url.path
                if link_domain:
                    if link_domain.startswith('www.'):
                        link_domain = link_domain[4:]
                    if link_domain in domains:
                        number = domains[link_domain]
                        if include_numbers and number is not None:
                            matched_lines.append((original_line, number))
                        else:
                            matched_lines.append((original_line,))

    if export_csv:
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            if include_numbers:
                writer.writerow(['URL', 'Number'])
            else:
                writer.writerow(['URL'])
            for items in matched_lines:
                writer.writerow(items)
    else:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for items in matched_lines:
                f_out.write('\t'.join(items) + '\n')

def merge_files(directory, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
    print(f"Все текстовые файлы из каталога {directory} объединены в файл {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python dsu.py режим [аргументы]")
        print("Режимы:")
        print("1 - Разбить файл на несколько файлов по количеству строк")
        print("    Аргументы: входной_файл максимальное_количество_строк")
        print("2 - Извлечь домены из ссылок")
        print("    Аргументы: входной_файл")
        print("3 - Сравнить два файла (домены и ссылки)")
        print("    Аргументы: файл_домены файл_ссылки выходной_файл [-in] [-csv]")
        print("4 - Объединить текстовые файлы из каталога в один файл")
        print("    Аргументы: путь_к_каталогу")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "1":
        if len(sys.argv) != 4:
            print("Для режима 1 необходимо указать входной файл и максимальное количество строк.")
            print("Использование: python dsu.py 1 входной_файл количество_строк")
            sys.exit(1)
        input_filename = sys.argv[2]
        try:
            max_lines = int(sys.argv[3])
            split_file(input_filename, max_lines)
            print("Файл успешно разбит на части.")
        except ValueError:
            print("Максимальное количество строк должно быть числом.")
    elif mode == "2":
        if len(sys.argv) != 3:
            print("Для режима 2 необходимо указать входной файл.")
            print("Использование: python dsu.py 2 входной_файл")
            sys.exit(1)
        input_filename = sys.argv[2]
        output_filename = os.path.splitext(input_filename)[0] + '_domains.txt'
        extract_domains(input_filename, output_filename)
        print(f"Домены сохранены в файл {output_filename}")
    elif mode == "3":
        domains_file = None
        links_file = None
        output_filename = None
        include_numbers = False
        export_csv = False

        args = sys.argv[2:]

        if len(args) < 3:
            print("Для режима 3 необходимо указать файл с доменами, файл с ссылками и выходной файл.")
            print("Дополнительные опции: [-in] [-csv]")
            print("Использование: python dsu.py 3 файл_домены файл_ссылки выходной_файл [опции]")
            sys.exit(1)

        domains_file = args[0]
        links_file = args[1]
        output_filename = args[2]
        optional_args = args[3:]

        if '-in' in optional_args:
            include_numbers = True
            optional_args.remove('-in')

        if '-csv' in optional_args:
            export_csv = True
            optional_args.remove('-csv')

        if optional_args:
            print(f"Неизвестные опции: {' '.join(optional_args)}")
            sys.exit(1)

        compare_files(domains_file, links_file, output_filename, include_numbers, export_csv)

        if export_csv:
            print(f"Результаты сохранены в CSV файл {output_filename}.")
        else:
            print(f"Результаты сохранены в файл {output_filename}")

    elif mode == "4":
        if len(sys.argv) != 3:
            print("Для режима 4 необходимо указать путь к каталогу.")
            print("Использование: python dsu.py 4 путь_к_каталогу")
            sys.exit(1)
        directory_path = sys.argv[2]
        output_filename = 'merged.txt'
        merge_files(directory_path, output_filename)
    else:
        print("Неверный режим работы. Допустимые режимы: 1, 2, 3 или 4.")
