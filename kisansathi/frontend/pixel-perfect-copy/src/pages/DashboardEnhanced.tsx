import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/context/LanguageContext";
import { LogOut, Settings, User } from "lucide-react";

interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
}

const DashboardEnhanced = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get user from localStorage or API
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error("Error parsing user data:", error);
      }
    }
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/auth");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>{language === "en" ? "Loading..." : "लोड हो रहा है..."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              {language === "en" ? "Dashboard" : "डैशबोर्ड"}
            </h1>
            <p className="text-gray-600 mt-2">
              {language === "en" ? "Welcome back!" : "स्वागत है!"}
            </p>
          </div>
          <Button variant="outline" onClick={handleLogout} className="gap-2">
            <LogOut className="w-4 h-4" />
            {language === "en" ? "Logout" : "लॉगआउट"}
          </Button>
        </div>

        {/* User Profile Card */}
        {user && (
          <Card className="mb-8 bg-white shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                {language === "en" ? "Profile" : "प्रोफाइल"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">
                    {language === "en" ? "Name" : "नाम"}
                  </p>
                  <p className="text-lg font-semibold">{user.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">
                    {language === "en" ? "Email" : "ईमेल"}
                  </p>
                  <p className="text-lg font-semibold">{user.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">
                    {language === "en" ? "Role" : "भूमिका"}
                  </p>
                  <p className="text-lg font-semibold capitalize">{user.role}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => navigate("/crop")}>
            <CardHeader>
              <CardTitle className="text-lg">
                {language === "en" ? "Crop Recommendation" : "फसल सिफारिश"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {language === "en" ? "Get personalized crop recommendations" : "व्यक्तिगत फसल सिफारिशें प्राप्त करें"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => navigate("/fertilizer")}>
            <CardHeader>
              <CardTitle className="text-lg">
                {language === "en" ? "Fertilizer Guide" : "खाद गाइड"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {language === "en" ? "Learn about fertilizer recommendations" : "खाद की सिफारिशें जानें"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => navigate("/disease")}>
            <CardHeader>
              <CardTitle className="text-lg">
                {language === "en" ? "Disease Detection" : "रोग पहचान"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {language === "en" ? "Detect crop diseases early" : "फसल के रोगों का जल्दी पता लगाएं"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => navigate("/weather")}>
            <CardHeader>
              <CardTitle className="text-lg">
                {language === "en" ? "Weather Alerts" : "मौसम सतर्कता"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {language === "en" ? "Get real-time weather updates" : "रीयल-टाइम मौसम अपडेट प्राप्त करें"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => navigate("/reminders")}>
            <CardHeader>
              <CardTitle className="text-lg">
                {language === "en" ? "Smart Reminders" : "स्मार्ट रिमाइंडर"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {language === "en" ? "Set farming reminders" : "खेती के रिमाइंडर सेट करें"}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={() => navigate("/community")}>
            <CardHeader>
              <CardTitle className="text-lg">
                {language === "en" ? "Community" : "समुदाय"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                {language === "en" ? "Connect with other farmers" : "अन्य किसानों से जुड़ें"}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Settings */}
        <div className="mt-8 flex justify-center">
          <Button variant="outline" className="gap-2" onClick={() => navigate("/profile")}>
            <Settings className="w-4 h-4" />
            {language === "en" ? "Settings" : "सेटिंग्स"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DashboardEnhanced;
