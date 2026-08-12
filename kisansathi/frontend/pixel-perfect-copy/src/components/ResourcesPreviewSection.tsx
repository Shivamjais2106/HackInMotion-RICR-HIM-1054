import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Download, Sprout } from 'lucide-react';
import bookOrganic from '@/assets/book-organic.jpg';
import bookCrop from '@/assets/book-crop.jpg';
import bookWater from '@/assets/book-water.jpg';
import bookSmart from '@/assets/book-smart.jpg';

const ResourcesPreviewSection = () => {
  const featuredBooks = [
    {
      title: 'Organic Farming Guide',
      author: 'Dr. Rajesh Kumar',
      category: 'जैविक खेती',
      cover: bookOrganic,
      desc: 'जैविक खेती की पूरी जानकारी — मिट्टी की तैयारी से लेकर फसल कटाई तक।',
      pdfFile: 'Jaivik kheti.pdf',
    },
    {
      title: 'Crop Management',
      author: 'Prof. Sunita Sharma',
      category: 'फसल प्रबंधन',
      cover: bookCrop,
      desc: 'फसल प्रबंधन के आधुनिक तरीके — मिट्टी परीक्षण और उर्वरक प्रबंधन।',
      pdfFile: 'Phal-Phool-Sept-Oct 2020.pdf',
    },
    {
      title: 'Water Management',
      author: 'Dr. Anil Verma',
      category: 'जल प्रबंधन',
      cover: bookWater,
      desc: 'सिंचाई और जल प्रबंधन की तकनीकें — ड्रिप इरिगेशन और स्प्रिंकलर सिस्टम।',
      pdfFile: 'SABJIX16Xpage.pdf',
    },
    {
      title: 'Smart Agriculture',
      author: 'Dr. Priya Patel',
      category: 'स्मार्ट खेती',
      cover: bookSmart,
      desc: 'ड्रोन, IoT सेंसर और AI तकनीक से खेती में क्रांति।',
      pdfFile: 'SABJIX16Xpage - Copy.pdf',
    },
  ];

  const handleReadPDF = (book: typeof featuredBooks[0]) => {
    if (book.pdfFile) {
      const encodedFileName = encodeURIComponent(book.pdfFile);
      window.open(`/pdfs/${encodedFileName}`, '_blank');
    }
  };

  const handleDownloadPDF = (book: typeof featuredBooks[0]) => {
    if (book.pdfFile) {
      const link = document.createElement('a');
      const encodedFileName = encodeURIComponent(book.pdfFile);
      link.href = `/pdfs/${encodedFileName}`;
      link.download = book.pdfFile;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <section className="py-12 sm:py-16 md:py-20 lg:py-24 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-10 sm:mb-12 md:mb-16">
          <div className="flex items-center justify-center gap-2 mb-3 sm:mb-4">
            <Sprout className="w-6 h-6 sm:w-7 sm:h-7 text-green-600" />
            <p className="text-xs sm:text-sm font-bold uppercase tracking-[0.15em] text-green-600">Learning Resources</p>
          </div>
          
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800 mb-3 sm:mb-4">
            किसान पुस्तकालय
          </h2>
          
          <p className="text-sm sm:text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
            खेती-किसानी की बेहतरीन किताबें — जैविक खेती, फसल प्रबंधन, जल संरक्षण और स्मार्ट कृषि पर विस्तृत जानकारी।
          </p>
        </div>

        {/* Books Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8 sm:mb-10 md:mb-12">
          {featuredBooks.map((book, idx) => (
            <div
              key={idx}
              className="group bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border border-blue-100"
            >
              {/* Book Cover */}
              <div className="relative aspect-[4/3] overflow-hidden bg-gray-200">
                <img
                  src={book.cover}
                  alt={book.title}
                  loading="lazy"
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* Category Badge */}
                <div className="absolute top-3 left-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                  {book.category}
                </div>
              </div>

              {/* Content */}
              <div className="p-4 sm:p-5">
                <h3 className="font-bold text-gray-800 text-sm sm:text-base line-clamp-2 mb-1">
                  {book.title}
                </h3>
                <p className="text-xs sm:text-sm text-green-600 font-semibold mb-3">
                  {book.author}
                </p>
                <p className="text-xs sm:text-sm text-gray-600 line-clamp-2 mb-4">
                  {book.desc}
                </p>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleReadPDF(book)}
                    className="flex-1 flex items-center justify-center gap-1 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white py-2 rounded-lg font-semibold text-xs sm:text-sm transition-all duration-300 transform hover:scale-105"
                  >
                    <BookOpen className="w-4 h-4" />
                    <span className="hidden sm:inline">Read</span>
                  </button>
                  <button 
                    onClick={() => handleDownloadPDF(book)}
                    className="flex-1 flex items-center justify-center gap-1 border-2 border-green-500 text-green-600 hover:bg-green-50 py-2 rounded-lg font-semibold text-xs sm:text-sm transition-all duration-300"
                  >
                    <Download className="w-4 h-4" />
                    <span className="hidden sm:inline">PDF</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 rounded-xl sm:rounded-2xl p-6 sm:p-8 md:p-10 text-white shadow-lg">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 sm:gap-6">
            <div>
              <h3 className="text-xl sm:text-2xl md:text-3xl font-bold mb-2">
                6+ किताबें और गाइड
              </h3>
              <p className="text-sm sm:text-base text-white/90">
                सभी किताबें मुफ्त में डाउनलोड करें और अपनी खेती को बेहतर बनाएं।
              </p>
            </div>
            <Link
              to="/resources"
              className="inline-flex items-center gap-2 px-6 sm:px-8 py-3 sm:py-4 bg-white text-green-600 font-bold rounded-lg hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-lg whitespace-nowrap text-sm sm:text-base"
            >
              सभी किताबें देखें
              <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ResourcesPreviewSection;
