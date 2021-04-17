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

    ignored_fword = ["캐시", "캐쉬", "010"]
    # 여기 단어가 포함된 모든 비속어를 제거하고, 여기 단어만 추가함.
    # 이 단어가 포함된 것 만으로도 비속어이고, 접두어나 접미사 이외로도 쓸 수 있는 경우에 해당됨.
    compressed_fword = [
        "섹스",
        "sex",
        "포르노",
        "porno",
        "몰카",
        "molca",
        "와레즈",
        "warez",
        "성인용품",
    ]

    words = set()
    with open(args.input_file, "r", encoding="utf-8", newline="") as file:
        csv_reader = csv.reader(file, skipinitialspace=True)
        for row in csv_reader:
            for elem in row:
                elem = elem.strip().casefold()
                if any(ignored in elem for ignored in ignored_fword):
                    continue
                if any(compressed in elem for compressed in compressed_fword):
                    continue
                words.add(elem)
    words.update(compressed_fword)
    sorted_words = sorted(words)
    with open(args.output_file, "w", encoding="utf-8", newline="") as file:
        csv_writer = csv.writer(file)
        for word in sorted_words:
            csv_writer.writerow([word])


if __name__ == "__main__":
    main()
