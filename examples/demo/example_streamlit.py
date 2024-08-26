import streamlit as st
from namedivider import BasicNameDivider, GBDTNameDivider
from pathlib import Path
Path("~/.cache").expanduser().mkdir(exist_ok=True)


@st.cache_resource
def get_basic_name_divider():
    basic_divider = BasicNameDivider()
    return basic_divider


@st.cache_resource
def get_gbdt_name_divider():
    gbdt_divider = GBDTNameDivider()
    return gbdt_divider


def main():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        option = st.selectbox(
            'Language',
            ("Japanese", 'English'))

    basic_divider = get_basic_name_divider()
    gbdt_divider = get_gbdt_name_divider()

    if option == "Japanese":
        st.title("NameDivider Demo")
        st.write("NameDividerは、姓名が連結している日本語の名前を姓と名に分割するツールです。")
        st.write("https://github.com/rskmoi/namedivider-python")
        st.write("左側のテキストエリアに名前を入力すると、右側に分割された名前が出力されます。")
        mode_select = "分割手法を選択してください"
        mode_basic = "BasicNameDivider(速いけれど、精度が99.2%)"
        mode_gbdt = "GBDTNameDivider(遅いけれど、精度が99.9%)"
        input_label = "入力"
        output_label = "結果"
        too_many_error = "一度に分割できる名前の数は500人までです"
        info = 'このページはNameDividerの使用感をお伝えするためのデモページです。\n ' \
            '1. このページの使用により生じる不利益について作者は一切責任を負わないものとします。 \n ' \
            '2. このページは任意のタイミングで非公開になる可能性が有ります。 \n ' \
            '3. 入力された名前は保存をしておらず、作者が確認することはできません。'
    elif option == "English":
        st.title("NameDivider Demo")
        st.write("NameDivider is a tool for dividing the Japanese full name into a family name and a given name.")
        st.write("https://github.com/rskmoi/namedivider-python")
        st.write("Entering names in the text area on the left side will output the divided names on the right side.")
        mode_select = "Please select a division method."
        mode_basic = "BasicNameDivider(Fast, but accuracy is 99.2%)"
        mode_gbdt = "GBDTNameDivider(Slow, but accuracy is 99.9%)"
        input_label = "Input undivided names."
        output_label = "Divided names are shown here."
        too_many_error = "The number of names that can be divided at one time is limited to 500"
        info = 'This page is a demo page to show how NameDivider works.\n ' \
            '1. The author assumes no responsibility for any disadvantages that may result from the use of this page. \n ' \
            '2. This page may become private at any time. \n ' \
            '3. The name entered is not saved and cannot be confirmed by the author.'

    else:
        raise ValueError

    mode = st.radio(
        mode_select,
        (mode_basic, mode_gbdt))

    input_area, output_area = st.columns(2)
    undivided_names = input_area.text_area(input_label,
                                           height=500,
                                           placeholder="菅義偉\n岸田文雄\n鳩山由紀夫")
    divided_names = []
    undivided_names_list = undivided_names.split("\n")
    if len(undivided_names_list) > 500:
        st.error(too_many_error)
    for _name in undivided_names_list:
        if len(_name) < 2:
            continue
        if mode == mode_basic:
            _divided_name = str(basic_divider.divide_name(_name))
        elif mode == mode_gbdt:
            _divided_name = str(gbdt_divider.divide_name(_name))
        else:
            raise ValueError
        divided_names.append(_divided_name)
    output_area.text_area(label=output_label,
                          value="\n".join(divided_names),
                          height=500,
                          placeholder="菅 義偉\n岸田 文雄\n鳩山 由紀夫")

    st.info(info)


if __name__ == '__main__':
    main()