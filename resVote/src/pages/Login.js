import { Button, Form, Input } from "antd";
import bcrypt from "bcryptjs";
import { useNavigate } from "react-router-dom";

async function submitValues(event) {
    const username = event.username;
    const password = event.password

    const salt = await bcrypt.genSalt();
    const hashedPassword = await bcrypt.hash(password, salt);
    const jwt = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username, hashedPassword})
    });

    if (jwt) {
        localStorage.setItem("authToken", jwt);
    }
    else {
        failedSubmission();
    }
}

function failedSubmission() {
    return false;
}

export default function Login() {
    const navigate = useNavigate();
    return (
        <>
            <h1>Login Page</h1>
            <Form
                name="basic"
                labelCol={{
                span: 8,
                }}
                wrapperCol={{
                span: 16,
                }}
                style={{
                maxWidth: 600,
                }}
                initialValues={{
                remember: true,
                }}
                onFinish={submitValues}
                onFinishFailed={failedSubmission}
                autoComplete="off"
            >
                <Form.Item
                label="Username"
                name="username"
                rules={[
                    {
                    required: true,
                    message: 'Please input your username!',
                    },
                ]}
                >
                <Input />
                </Form.Item>

                <Form.Item
                label="Password"
                name="password"
                rules={[
                    {
                    required: true,
                    message: 'Please input your password!',
                    },
                ]}
                >
                <Input.Password />
                </Form.Item>

                <Form.Item label={null}>
                <Button type="primary" htmlType="submit">
                    Submit
                </Button>
                </Form.Item>
            </Form>
        </>
    )
}