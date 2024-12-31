import streamlit as st


st.set_page_config(page_title="Rain prediction",page_icon=":umbrella_with_rain_drops:", layout ="wide")

#Local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")

#Header
st.subheader("Rain prediction web application :umbrella_with_rain_drops:")
st.title("By Pham Tien Dat and Nguyen Tran Hoi Thang")
st.write("Testing")
st.write("[Our repository](https://github.com/3ckk0n/Weather_Prediction)")

#Form
with st.container():
    st.write("---")
    st.header("Get In Touch With Me!")
    st.write("##")

    # Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
    contact_form = """
    <form action="https://formsubmit.co/75fe57395da9225afff667028946275e" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here" required></textarea>
        <button type="submit">Send</button>
    </form>
    """
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown(contact_form, unsafe_allow_html=True)
    with right_column:
        st.empty()