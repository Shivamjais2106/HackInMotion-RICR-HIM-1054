import { ShoppingCart, ExternalLink } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const ShopPreview = () => {
  const { t } = useLanguage();
  
  const products = [
    { 
      name: "Neem Oil (Organic Pesticide)", 
      price: "₹250-350", 
      image: "https://m.media-amazon.com/images/I/513Udn-rz-L._AC_UL480_FMwebp_QL65_.jpg",
      amazon: "https://www.amazon.in/s?k=neem+oil+pesticide",
    },
    { 
      name: "DAP Fertilizer (18:46:0)", 
      price: "₹600-800/50kg", 
      image: "https://m.media-amazon.com/images/I/71ihvG9N7FL._AC_UL480_FMwebp_QL65_.jpg",
      amazon: "https://www.amazon.in/s?k=DAP+fertilizer",
    },
    { 
      name: "Urea Fertilizer (46% N)", 
      price: "₹500-700/50kg", 
      image: "https://m.media-amazon.com/images/I/616mfGRR5gL._AC_UL480_FMwebp_QL65_.jpg",
      amazon: "https://www.amazon.in/s?k=urea+fertilizer",
    },
    { 
      name: "Vermicompost (Organic)", 
      price: "₹150-250/kg", 
      image: "https://m.media-amazon.com/images/I/71zxEAIaI7L._AC_UL480_FMwebp_QL65_.jpg",
      amazon: "https://www.amazon.in/s?k=vermicompost+organic",
    },
  ];

  return (
    <section className="py-16 md:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        {/* Header */}
        <div className="text-center mb-12">
          <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">{t('shop.featured')}</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3 mb-4">
            {t('shop.title')}
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            {t('shop.subtitle')}
          </p>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {products.map((product, index) => (
            <div key={index} className="group cursor-pointer">
              <div className="bg-gradient-to-br from-green-100 to-teal-100 rounded-2xl overflow-hidden aspect-square flex items-center justify-center p-4 hover:shadow-lg transition-shadow mb-4">
                <img 
                  src={product.image} 
                  alt={product.name}
                  className="w-full h-full object-cover rounded-lg"
                  onError={(e) => {
                    e.currentTarget.src = "https://via.placeholder.com/300?text=" + encodeURIComponent(product.name.split('(')[0].trim());
                  }}
                />
              </div>
              <div className="text-center">
                <h3 className="font-heading text-lg font-bold text-eco-green-dark mb-1">
                  {product.name}
                </h3>
                <p className="text-muted-foreground font-semibold text-green-600 mb-3">
                  {product.price}
                </p>
                
                {/* Buy Button */}
                <a
                  href={product.amazon}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-4 rounded-lg transition-all text-sm w-full"
                >
                  <ShoppingCart className="w-4 h-4" />
                  {t('shop.buyAmazon')}
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* View All Button */}
        <div className="text-center">
          <a
            href="/shop"
            className="inline-flex items-center gap-3 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-bold px-8 py-4 rounded-full transition-all shadow-lg hover:shadow-xl"
          >
            {t('shop.viewAll')}
            <span className="bg-white text-eco-green-dark rounded-full w-6 h-6 flex items-center justify-center text-sm">→</span>
          </a>
        </div>
      </div>
    </section>
  );
};

export default ShopPreview;
