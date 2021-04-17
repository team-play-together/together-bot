import argparse
import csv
import pathlib


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="비속어 데이터가 담긴 파일을 bot에서 읽을 수 있도록 수정함.")
    parser.add_argument("input_file", type=pathlib.Path)
    parser.add_argument("output_file", type=pathlib.Path)
    return parser


# 욕설 필터링 데이터 가공용 스크립트
# csv에 행렬에 상관없이 들어있는 단어들의 앞뒤공백 제거와 대소문자 구분 제거를 한 후,
# 콜론으로만 구분하도록 파일 크기를 줄임
def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()

    words = set()
    with open(args.input_file, "r", encoding="utf-8", newline="") as file:
        csv_reader = csv.reader(file, skipinitialspace=True)
        for row in csv_reader:
            for elem in row:
                elem = elem.strip().casefold()
                words.add(elem)

    with open(args.output_file, "w", encoding="utf-8", newline="") as file:
        csv_writer = csv.writer(file)
        for word in words:
            csv_writer.writerow([word])


if __name__ == "__main__":
    main()
