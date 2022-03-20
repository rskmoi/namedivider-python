import streamlit as st
from namedivider import NameDivider


def main():
    divider = NameDivider()
    st.title("NameDivider Demo")
    st.write("NameDivider is a tool for dividing the Japanese full name into a family name and a given name.")
    st.write("Enter undivided names and see if it divides properly!")

    input_area, output_area = st.columns(2)
    undivided_names = input_area.text_area("Input undivided names.",
                                           height=500,
                                           placeholder="菅義偉\n岸田文雄\n鳩山由紀夫")
    divided_names = []
    for _name in undivided_names.split("\n"):
        if len(_name) < 2:
            continue
        divided_names.append(str(divider.divide_name(_name)))
    output_area.text_area(label="Divided names are shown here.",
                          value="\n".join(divided_names),
                          height=500,
                          placeholder="菅 義偉\n岸田 文雄\n鳩山 由紀夫")


if __name__ == '__main__':
    main()