import sys

def rewrite_login(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    start_str = "def login_screen():"
    end_str = "if \"user_id\" not in st.session_state:"
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find start or end bounds.")
        sys.exit(1)
        
    new_login_func = """def login_screen():
    import random
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>InvestIQ</h1>", unsafe_allow_html=True)
        
        if st.session_state.get("show_forgot_password", False):
            st.markdown("### Reset Password")
            if "reset_otp_pending" not in st.session_state:
                reset_user = st.text_input("Username", key="reset_user")
                new_reset_pass = st.text_input("New Password", type="password", key="reset_pass")
                if st.button("Send Reset OTP", use_container_width=True, type="primary"):
                    if not reset_user or not new_reset_pass:
                        st.error("Please fill all fields.")
                    else:
                        email = get_user_email(reset_user)
                        if email:
                            otp_code = str(random.randint(100000, 999999))
                            html = f"<h3>InvestIQ Password Reset</h3><p>Your password reset code is: <b>{otp_code}</b></p>"
                            with st.spinner("Sending OTP to registered email..."):
                                success, err_msg = send_alert_email(email, "InvestIQ Password Reset", html)
                                if success:
                                    st.session_state["reset_otp_pending"] = True
                                    st.session_state["reset_otp_code"] = otp_code
                                    st.session_state["reset_pending_user"] = reset_user
                                    st.session_state["reset_pending_pass"] = new_reset_pass
                                    st.rerun()
                                else:
                                    st.error("Failed to send email.")
                        else:
                            st.error("Username not found or no email associated.")
            else:
                st.info("OTP sent to your registered email.")
                entered_reset_otp = st.text_input("Enter 6-digit OTP", key="entered_reset_otp")
                c1, c2 = st.columns(2)
                if c1.button("Reset Password", type="primary", use_container_width=True):
                    if entered_reset_otp == st.session_state["reset_otp_code"]:
                        if update_password(st.session_state["reset_pending_user"], st.session_state["reset_pending_pass"]):
                            st.success("Password updated successfully! Please log in.")
                            for k in ["reset_otp_pending", "reset_otp_code", "reset_pending_user", "reset_pending_pass"]:
                                if k in st.session_state: del st.session_state[k]
                            st.session_state["show_forgot_password"] = False
                        else:
                            st.error("Failed to update password.")
                    else:
                        st.error("Invalid OTP.")
                if c2.button("Cancel Reset", use_container_width=True):
                    for k in ["reset_otp_pending", "reset_otp_code", "reset_pending_user", "reset_pending_pass"]:
                        if k in st.session_state: del st.session_state[k]
                    st.rerun()
            
            st.divider()
            if st.button("Back to Login", use_container_width=True):
                st.session_state["show_forgot_password"] = False
                st.rerun()
                
        else:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.markdown("### Welcome Back")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                
                st.write("") # spacer
                
                if st.button("Login", use_container_width=True, type="primary"):
                    user = verify_user(username, password)
                    if user:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["username"] = user["username"]
                        st.session_state["email"] = user["email"]
                        st.session_state["role"] = user["role"]
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                
                st.write("") # spacer
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state["show_forgot_password"] = True
                    st.rerun()
                        
            with tab2:
                st.markdown("### Create Account")
                if "otp_pending" not in st.session_state:
                    new_user = st.text_input("New Username", key="signup_user")
                    new_email = st.text_input("Email Address", key="signup_email")
                    new_pass = st.text_input("New Password", type="password", key="signup_pass")
                    if st.button("Send OTP", use_container_width=True, type="primary"):
                        if not new_email or "@" not in new_email:
                            st.error("Please enter a valid email address.")
                        elif not new_user or not new_pass:
                            st.error("Please fill all fields.")
                        else:
                            otp_code = str(random.randint(100000, 999999))
                            html = f"<h3>InvestIQ Verification</h3><p>Your verification code is: <b>{otp_code}</b></p>"
                            with st.spinner("Sending OTP via Email..."):
                                success, err_msg = send_alert_email(new_email, "InvestIQ Verification Code", html)
                                if success:
                                    st.session_state["otp_pending"] = True
                                    st.session_state["otp_code"] = otp_code
                                    st.session_state["pending_user"] = new_user
                                    st.session_state["pending_email"] = new_email
                                    st.session_state["pending_pass"] = new_pass
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send OTP. Check SMTP settings. Error: {err_msg}")
                else:
                    st.info(f"An OTP was sent to **{st.session_state['pending_email']}**.")
                    entered_otp = st.text_input("Enter 6-digit OTP", key="entered_otp")
                    c1, c2 = st.columns(2)
                    if c1.button("Verify & Sign Up", type="primary", use_container_width=True):
                        if entered_otp == st.session_state["otp_code"]:
                            if register_user(st.session_state["pending_user"], st.session_state["pending_email"], st.session_state["pending_pass"]):
                                st.success("Account created successfully! You can now log in.")
                                for k in ["otp_pending", "otp_code", "pending_user", "pending_email", "pending_pass"]:
                                    if k in st.session_state: del st.session_state[k]
                            else:
                                st.error("Username already exists or database error.")
                        else:
                            st.error("Invalid OTP. Try again.")
                    if c2.button("Cancel", use_container_width=True):
                        for k in ["otp_pending", "otp_code", "pending_user", "pending_email", "pending_pass"]:
                            if k in st.session_state: del st.session_state[k]
                        st.rerun()

"""
    
    new_content = content[:start_idx] + new_login_func + content[end_idx:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
if __name__ == '__main__':
    rewrite_login('src/app_ui.py')
