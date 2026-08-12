import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { ShoppingCart, ExternalLink, Mic } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/context/LanguageContext";
import React from "react";

const products = [
  // ===== RECOMMENDED FERTILIZERS (10 Types) =====
  { 
    name: "Balanced NPK Fertilizer (10:10:10)", 
    price: "₹400-600/50kg", 
    image: "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=balanced+NPK+fertilizer+10:10:10",
    flipkart: "https://www.flipkart.com/search?q=balanced+NPK+fertilizer",
    category: "Recommended"
  },
  { 
    name: "Compost (Organic Matter)", 
    price: "₹200-350/50kg", 
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad576?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=compost+organic+fertilizer",
    flipkart: "https://www.flipkart.com/search?q=compost+organic",
    category: "Recommended"
  },
  { 
    name: "DAP Fertilizer (18:46:0)", 
    price: "₹600-800/50kg", 
    image: "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=DAP+fertilizer+18:46",
    flipkart: "https://www.flipkart.com/search?q=DAP+fertilizer",
    category: "Recommended"
  },
  { 
    name: "General Purpose Fertilizer", 
    price: "₹350-550/50kg", 
    image: "https://images.unsplash.com/photo-1584622181563-430f63602d4b?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=general+purpose+fertilizer",
    flipkart: "https://www.flipkart.com/search?q=general+purpose+fertilizer",
    category: "Recommended"
  },
  { 
    name: "Gypsum (Calcium Sulfate)", 
    price: "₹300-450/50kg", 
    image: "https://images.unsplash.com/photo-1585314062340-f4346add912b?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=gypsum+calcium+sulfate",
    flipkart: "https://www.flipkart.com/search?q=gypsum+fertilizer",
    category: "Recommended"
  },
  { 
    name: "Lime (Calcium Carbonate)", 
    price: "₹250-400/50kg", 
    image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=lime+calcium+carbonate+agricultural",
    flipkart: "https://www.flipkart.com/search?q=lime+fertilizer",
    category: "Recommended"
  },
  { 
    name: "Muriate of Potash (MOP 60% K2O)", 
    price: "₹700-900/50kg", 
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd64b73?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=muriate+of+potash+MOP",
    flipkart: "https://www.flipkart.com/search?q=muriate+of+potash",
    category: "Recommended"
  },
  { 
    name: "Organic Fertilizer (Vermicompost)", 
    price: "₹150-300/kg", 
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad576?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=organic+fertilizer+vermicompost",
    flipkart: "https://www.flipkart.com/search?q=organic+fertilizer",
    category: "Recommended"
  },
  { 
    name: "Urea Fertilizer (46% N)", 
    price: "₹500-700/50kg", 
    image: "https://m.media-amazon.com/images/I/617MOehEBaL._SX522_.jpg",
    amazon: "https://www.amazon.in/s?k=urea+fertilizer+46",
    flipkart: "https://www.flipkart.com/search?q=urea+fertilizer",
    category: "Recommended"
  },
  { 
    name: "Water Retaining Fertilizer", 
    price: "₹400-600/50kg", 
    image: "https://images.unsplash.com/photo-1576091160550-112173f7f869?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=water+retaining+fertilizer",
    flipkart: "https://www.flipkart.com/search?q=water+retaining+fertilizer",
    category: "Recommended"
  },

  // ===== OTHER PRODUCTS =====
  { 
    name: "Neem Oil (Organic Pesticide)", 
    price: "₹250-350", 
    image: "https://m.media-amazon.com/images/I/31Hjv+PFTtL._SX342_SY445_QL70_FMwebp_.jpg",
    amazon: "https://www.amazon.in/s?k=neem+oil+pesticide",
    flipkart: "https://www.flipkart.com/search?q=neem+oil+pesticide",
    category: "Other"
  },
  { 
    name: "Carbofuran (Insecticide)", 
    price: "₹400-550", 
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd64b73?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=carbofuran+insecticide",
    flipkart: "https://www.flipkart.com/search?q=carbofuran+insecticide",
    category: "Other"
  },
  { 
    name: "Sulfur Powder (Fungicide)", 
    price: "₹200-300/kg", 
    image: "https://images.unsplash.com/photo-1585314062340-f4346add912b?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=sulfur+powder+fungicide",
    flipkart: "https://www.flipkart.com/search?q=sulfur+powder+fungicide",
    category: "Other"
  },
  { 
    name: "Copper Fungicide", 
    price: "₹350-500", 
    image: "https://images.unsplash.com/photo-1576091160550-112173f7f869?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=copper+fungicide",
    flipkart: "https://www.flipkart.com/search?q=copper+fungicide",
    category: "Other"
  },
  { 
    name: "Azospirillum Bio-Fertilizer", 
    price: "₹150-250/kg", 
    image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=azospirillum+biofertilizer",
    flipkart: "https://www.flipkart.com/search?q=azospirillum+biofertilizer",
    category: "Other"
  },
  { 
    name: "Zinc Sulfate (Micronutrient)", 
    price: "₹300-450/kg", 
    image: "https://images.unsplash.com/photo-1585314062340-f4346add912b?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=zinc+sulfate+micronutrient",
    flipkart: "https://www.flipkart.com/search?q=zinc+sulfate+micronutrient",
    category: "Other"
  },
  { 
    name: "Mancozeb Fungicide", 
    price: "₹400-600", 
    image: "https://images.unsplash.com/photo-1599599810694-b5ac4dd64b73?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=mancozeb+fungicide",
    flipkart: "https://www.flipkart.com/search?q=mancozeb+fungicide",
    category: "Other"
  },
  { 
    name: "Bacillus Thuringiensis (Bt)", 
    price: "₹200-350/kg", 
    image: "https://images.unsplash.com/photo-1576091160550-112173f7f869?w=400&h=400&fit=crop",
    amazon: "https://www.amazon.in/s?k=bacillus+thuringiensis+bt",
    flipkart: "https://www.flipkart.com/search?q=bacillus+thuringiensis+bt",
    category: "Other"
  },
];

const ShopPage = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [filter, setFilter] = React.useState('all');
  
  const filteredProducts = filter === 'all' 
    ? products 
    : products.filter(p => p.category === filter);

  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Banner */}
      <section className="relative h-[400px] md:h-[480px] flex items-center">
        <img
          src="https://cdn.pixabay.com/photo/2016/09/21/04/46/barley-field-1684052_1280.jpg"
          alt="Shop Hero"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40" />
        <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-16 w-full">
          <h1 className="font-heading text-5xl md:text-7xl font-bold text-primary-foreground mb-4">
            {t('shop.pageTitle')}
          </h1>
          <p className="text-primary-foreground/80 text-lg md:text-xl max-w-lg">
            {t('shop.pageSubtitle')}
          </p>
        </div>
      </section>

      {/* Filter Section */}
      <section className="py-8 bg-gradient-to-r from-green-50 to-teal-50 border-b border-green-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="flex flex-wrap gap-3 items-center">
            <span className="font-semibold text-gray-700">Filter:</span>
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'all'
                  ? 'bg-green-600 text-white shadow-md'
                  : 'bg-white text-gray-700 border border-gray-300 hover:border-green-600'
              }`}
            >
              All Products
            </button>
            <button
              onClick={() => setFilter('Recommended')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'Recommended'
                  ? 'bg-green-600 text-white shadow-md'
                  : 'bg-white text-gray-700 border border-gray-300 hover:border-green-600'
              }`}
            >
              ⭐ Recommended Fertilizers (10)
            </button>
            <button
              onClick={() => setFilter('Other')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'Other'
                  ? 'bg-green-600 text-white shadow-md'
                  : 'bg-white text-gray-700 border border-gray-300 hover:border-green-600'
              }`}
            >
              Other Products
            </button>
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section className="py-16 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredProducts.map((product, index) => (
              <div key={index} className="group cursor-pointer">
                {/* Recommended Badge */}
                {product.category === 'Recommended' && (
                  <div className="absolute top-2 right-2 bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-xs font-bold z-10">
                    ⭐ RECOMMENDED
                  </div>
                )}
                
                <div className="bg-gradient-to-br from-green-100 to-teal-100 rounded-2xl overflow-hidden aspect-square flex items-center justify-center p-4 hover:shadow-lg transition-shadow relative">
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className="w-full h-full object-cover rounded-lg"
                    onError={(e) => {
                      e.currentTarget.src = "https://via.placeholder.com/400?text=" + encodeURIComponent(product.name.split('(')[0].trim());
                    }}
                  />
                </div>
                <div className="text-center mt-5">
                  <h3 className="font-heading text-lg font-bold text-eco-green-dark">
                    {product.name}
                  </h3>
                  <p className="text-muted-foreground mt-1 font-semibold text-green-600">
                    {product.price}
                  </p>
                  
                  {/* Buy Buttons */}
                  <div className="flex gap-3 mt-4">
                    <a
                      href={product.amazon}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 inline-flex items-center justify-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-3 rounded-lg transition-all text-sm"
                    >
                      <ShoppingCart className="w-4 h-4" />
                      {t('shop.buyAmazon')}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    <a
                      href={product.flipkart}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-3 rounded-lg transition-all text-sm"
                    >
                      <ShoppingCart className="w-4 h-4" />
                      {t('shop.buyFlipkart')}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default ShopPage;
