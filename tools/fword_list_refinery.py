import csv


# 욕설 필터링 데이터 가공용 스크립트
# csv에 행렬에 상관없이 들어있는 단어들의 앞뒤공백 제거와 대소문자 구분 제거를 한 후,
# 콜론으로만 구분하도록 파일 크기를 줄임
def main():
    file_name = "data.csv"
    words = set()
    with open(file_name, "r", encoding="utf-8", newline="") as file:
        csv_reader = csv.reader(file, skipinitialspace=True)
        for row in csv_reader:
            for elem in row:
                elem = elem.strip().casefold()
                words.add(elem)

    with open("refined.csv", "w", encoding="utf-8") as file:
        for word in words:
            file.write(word)
            file.write(",")


if __name__ == "__main__":
    main()
