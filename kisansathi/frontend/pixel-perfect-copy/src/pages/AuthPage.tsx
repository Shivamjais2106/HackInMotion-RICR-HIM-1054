import { useState } from "react";
import { Eye, EyeOff, Phone, User, Mail, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getAPIBaseURL } from "@/utils/api";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useLanguage } from "@/context/LanguageContext";

const AuthPage = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  // Signup states
  const [signupStep, setSignupStep] = useState<"details" | "mobile">("details");
  
  const [formData, setFormData] = useState({
    name: "",
    password: "",
    mobileNo: "",
    username: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError("");
  };

  // SIGNUP - Step 1: Name + Password
  const handleSignupStep1 = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.name.trim()) {
      setError("Please enter your name");
      return;
    }

    if (!formData.password || formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    // Move to step 2
    setSignupStep("mobile");
  };

  // SIGNUP - Step 2: Mobile Number
  const handleSignupStep2 = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!formData.mobileNo || formData.mobileNo.length !== 10) {
        setError("Please enter a valid 10-digit mobile number");
        setLoading(false);
        return;
      }

      // Username = Name
      const username = formData.name;

      // Call backend to register
      const response = await fetch(`${getAPIBaseURL()}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          username: username,
          email: `${formData.mobileNo}@kisansathi.local`,
          mobile: formData.mobileNo,
          password: formData.password,
          agriculture_type: "Crop Farming",
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store JWT token and user info
        localStorage.setItem("access_token", data.user_id);
        localStorage.setItem("token", data.user_id);
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("user_name", formData.name);
        localStorage.setItem("username", username);
        localStorage.setItem("token_type", "Bearer");
        
        setSuccess("Account created successfully! Redirecting...");
        setTimeout(() => {
          navigate("/");
        }, 1500);
      } else {
        setError(data.error || "Registration failed");
      }
    } catch (err) {
      setError("Connection error. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // LOGIN - Mobile + Password
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!formData.mobileNo || formData.mobileNo.length !== 10) {
        setError("Please enter a valid 10-digit mobile number");
        setLoading(false);
        return;
      }

      if (!formData.password) {
        setError("Please enter your password");
        setLoading(false);
        return;
      }

      const response = await fetch(`${getAPIBaseURL()}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mobile: formData.mobileNo,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store JWT token and user info
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("token", data.user_id);
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("user_name", data.name);
        localStorage.setItem("username", data.username || data.name);
        localStorage.setItem("token_type", data.token_type || "Bearer");
        
        setSuccess("Login successful! Redirecting...");
        setTimeout(() => {
          navigate("/");
        }, 1500);
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      setError("Connection error. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetSignup = () => {
    setSignupStep("details");
    setFormData({
      name: "",
      password: "",
      mobileNo: "",
      username: "",
    });
    setError("");
    setSuccess("");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 via-white to-green-50">
      <Navbar />

      {/* Hero Section */}
      <section className="relative py-16 bg-gradient-to-r from-eco-green via-eco-green-dark to-teal-700 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative max-w-7xl mx-auto px-6 lg:px-16">
          <div className="text-center">
            <h1 className="font-heading text-4xl md:text-5xl font-bold mb-4">
              {t('auth.title')}
            </h1>
            <p className="text-white/80 text-lg max-w-2xl mx-auto">
              {t('auth.subtitle')}
            </p>
          </div>
        </div>
      </section>

      {/* Auth Container */}
      <section className="flex-1 py-16 px-6">
        <div className="max-w-md mx-auto">
          {/* Toggle Buttons */}
          <div className="flex gap-3 mb-8 bg-white rounded-xl p-1 shadow-md">
            <button
              onClick={() => {
                setIsLogin(true);
                resetSignup();
              }}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
                isLogin
                  ? "bg-gradient-to-r from-eco-green to-teal-600 text-white shadow-lg"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {t('auth.login')}
            </button>
            <button
              onClick={() => {
                setIsLogin(false);
                resetSignup();
              }}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
                !isLogin
                  ? "bg-gradient-to-r from-eco-green to-teal-600 text-white shadow-lg"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {t('auth.signup')}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm font-medium">❌ {error}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700 text-sm font-medium">✅ {success}</p>
            </div>
          )}

          {/* Form Card */}
          <div className="bg-white rounded-2xl p-8 shadow-xl border border-green-100">
            {isLogin ? (
              // LOGIN FORM
              <>
                <h2 className="text-2xl font-bold text-eco-green-dark mb-2 text-center">
                  {t('auth.welcome')}
                </h2>
                <p className="text-center text-gray-600 text-sm mb-6">
                  Login with your mobile number and password
                </p>

                <form onSubmit={handleLogin} className="space-y-4">
                  {/* Mobile Number */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <Phone className="inline w-4 h-4 mr-2" />
                      Mobile Number
                    </label>
                    <input
                      type="tel"
                      name="mobileNo"
                      value={formData.mobileNo}
                      onChange={handleChange}
                      placeholder="10-digit mobile number"
                      pattern="[0-9]{10}"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-eco-green focus:ring-2 focus:ring-eco-green/20 focus:outline-none transition"
                      required
                    />
                  </div>

                  {/* Password */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      <Lock className="inline w-4 h-4 mr-2" />
                      Password
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword ? "text" : "password"}
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Enter your password"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-eco-green focus:ring-2 focus:ring-eco-green/20 focus:outline-none transition"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-3 text-gray-500 hover:text-eco-green transition"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 px-4 bg-gradient-to-r from-eco-green to-teal-600 text-white font-bold rounded-lg hover:shadow-lg hover:brightness-105 transition-all mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? "Processing..." : "Login"}
                  </button>
                </form>
              </>
            ) : (
              // SIGNUP FORM
              <>
                {signupStep === "details" ? (
                  // Step 1: Name & Password
                  <>
                    <h2 className="text-2xl font-bold text-eco-green-dark mb-2 text-center">
                      Create Your Account
                    </h2>
                    <p className="text-center text-gray-600 text-sm mb-6">
                      Step 1 of 2: Enter your name and password
                    </p>

                    <form onSubmit={handleSignupStep1} className="space-y-4">
                      {/* Name Field */}
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          <User className="inline w-4 h-4 mr-2" />
                          Full Name
                        </label>
                        <input
                          type="text"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          placeholder="Enter your full name"
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-eco-green focus:ring-2 focus:ring-eco-green/20 focus:outline-none transition"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          💡 This will be your username
                        </p>
                      </div>

                      {/* Password */}
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          <Lock className="inline w-4 h-4 mr-2" />
                          Password
                        </label>
                        <div className="relative">
                          <input
                            type={showPassword ? "text" : "password"}
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="At least 6 characters"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-eco-green focus:ring-2 focus:ring-eco-green/20 focus:outline-none transition"
                            required
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-3 text-gray-500 hover:text-eco-green transition"
                          >
                            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>

                      {/* Submit Button */}
                      <button
                        type="submit"
                        className="w-full py-3 px-4 bg-gradient-to-r from-eco-green to-teal-600 text-white font-bold rounded-lg hover:shadow-lg hover:brightness-105 transition-all mt-6"
                      >
                        Next Step →
                      </button>
                    </form>
                  </>
                ) : (
                  // Step 2: Mobile Number
                  <>
                    <h2 className="text-2xl font-bold text-eco-green-dark mb-2 text-center">
                      Add Mobile Number
                    </h2>
                    <p className="text-center text-gray-600 text-sm mb-6">
                      Step 2 of 2: Enter your mobile number
                    </p>

                    <form onSubmit={handleSignupStep2} className="space-y-4">
                      {/* Mobile Number */}
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          <Phone className="inline w-4 h-4 mr-2" />
                          Mobile Number
                        </label>
                        <input
                          type="tel"
                          name="mobileNo"
                          value={formData.mobileNo}
                          onChange={handleChange}
                          placeholder="10-digit mobile number"
                          pattern="[0-9]{10}"
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:border-eco-green focus:ring-2 focus:ring-eco-green/20 focus:outline-none transition"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          📱 This will be used for login
                        </p>
                      </div>

                      {/* Submit Button */}
                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 px-4 bg-gradient-to-r from-eco-green to-teal-600 text-white font-bold rounded-lg hover:shadow-lg hover:brightness-105 transition-all mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? "Creating Account..." : "Create Account"}
                      </button>

                      {/* Back Button */}
                      <button
                        type="button"
                        onClick={() => setSignupStep("details")}
                        className="w-full py-2 px-4 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition"
                      >
                        ← Back
                      </button>
                    </form>
                  </>
                )}
              </>
            )}
          </div>

          {/* Features */}
          <div className="mt-8 grid grid-cols-3 gap-3">
            <div className="p-4 bg-white rounded-xl shadow-md border border-green-100 text-center hover:shadow-lg transition">
              <p className="text-3xl mb-2">🌾</p>
              <p className="text-xs font-semibold text-gray-700">Smart Farming</p>
            </div>
            <div className="p-4 bg-white rounded-xl shadow-md border border-green-100 text-center hover:shadow-lg transition">
              <p className="text-3xl mb-2">📱</p>
              <p className="text-xs font-semibold text-gray-700">Easy Access</p>
            </div>
            <div className="p-4 bg-white rounded-xl shadow-md border border-green-100 text-center hover:shadow-lg transition">
              <p className="text-3xl mb-2">🤖</p>
              <p className="text-xs font-semibold text-gray-700">AI Assistant</p>
            </div>
          </div>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-teal-50 border-l-4 border-eco-green rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>💡 Tip:</strong> {isLogin ? "Use your mobile number to login" : "Your name will be your username"}
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default AuthPage;
