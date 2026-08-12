import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Search, BookOpen, Download, Sprout, X } from "lucide-react";
import bookOrganic from "@/assets/book-organic.jpg";
import bookCrop from "@/assets/book-crop.jpg";
import bookWater from "@/assets/book-water.jpg";
import bookSmart from "@/assets/book-smart.jpg";
import bookPest from "@/assets/book-pest.jpg";
import bookSeed from "@/assets/book-seed.jpg";
import heroImage from "@/assets/farm-hero.jpg";

const categories = [
  "सभी",
  "जैविक खेती",
  "फसल प्रबंधन",
  "जल प्रबंधन",
  "स्मार्ट खेती",
  "कीट नियंत्रण",
  "बीज विज्ञान",
];

const books = [
  {
    title: "Organic Farming Guide",
    author: "Dr. Rajesh Kumar",
    category: "जैविक खेती",
    pages: 245,
    cover: bookOrganic,
    desc: "जैविक खेती की पूरी जानकारी — मिट्टी की तैयारी से लेकर फसल कटाई तक। रासायनिक उर्वरकों के बिना बेहतर उपज कैसे पाएं।",
    pdfFile: "Jaivik kheti.pdf",
  },
  {
    title: "Crop Management",
    author: "Prof. Sunita Sharma",
    category: "फसल प्रबंधन",
    pages: 310,
    cover: bookCrop,
    desc: "फसल प्रबंधन के आधुनिक तरीके — मिट्टी परीक्षण, उर्वरक प्रबंधन और उत्पादकता बढ़ाने के उपाय।",
    pdfFile: "Phal-Phool-Sept-Oct 2020.pdf",
  },
  {
    title: "Water Management",
    author: "Dr. Anil Verma",
    category: "जल प्रबंधन",
    pages: 198,
    cover: bookWater,
    desc: "सिंचाई और जल प्रबंधन की तकनीकें — ड्रिप इरिगेशन, स्प्रिंकलर सिस्टम और वर्षा जल संचयन।",
    pdfFile: "SABJIX16Xpage.pdf",
  },
  {
    title: "Smart Agriculture",
    author: "Dr. Priya Patel",
    category: "स्मार्ट खेती",
    pages: 275,
    cover: bookSmart,
    desc: "ड्रोन, IoT सेंसर और AI तकनीक से खेती में क्रांति। स्मार्ट फार्मिंग के नवीनतम उपकरण और तकनीकें।",
    pdfFile: "Unnat Krishi, January - March, 2022 issue_2_0.pdf",
  },
  {
    title: "Pest Control",
    author: "Dr. Mohan Singh",
    category: "कीट नियंत्रण",
    pages: 220,
    cover: bookPest,
    desc: "कीट नियंत्रण के जैविक और रासायनिक तरीके। फसलों को कीटों और बीमारियों से बचाने के प्रभावी उपाय।",
    pdfFile: "Jaivik kheti.pdf",
  },
  {
    title: "Seed & Planting",
    author: "Prof. Kavita Gupta",
    category: "बीज विज्ञान",
    pages: 185,
    cover: bookSeed,
    desc: "बीज चयन, बीज उपचार और रोपण तकनीकें। सही बीज से बेहतर फसल कैसे उगाएं।",
    pdfFile: "Phal-Phool-Sept-Oct 2020.pdf",
  },
];

const ResourcesPage = () => {
  const [query, setQuery] = useState("");
  const [activeCat, setActiveCat] = useState("सभी");
  const [selectedBook, setSelectedBook] = useState<typeof books[0] | null>(null);

  const filtered = books.filter((b) => {
    const matchCat = activeCat === "सभी" || b.category === activeCat;
    const q = query.toLowerCase();
    const matchQ =
      !q ||
      b.title.toLowerCase().includes(q) ||
      b.author.toLowerCase().includes(q) ||
      b.category.toLowerCase().includes(q);
    return matchCat && matchQ;
  });

  const downloadPDF = (book: typeof books[0]) => {
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
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <header className="relative h-[420px] w-full overflow-hidden">
        <img
          src={heroImage}
          alt="किसान पुस्तकालय - खेती की किताबें"
          width={1920}
          height={768}
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/40" />
        <div className="relative z-10 flex h-full flex-col items-center justify-center px-4 text-center">
          <div className="flex items-center gap-3 drop-shadow-lg">
            <Sprout className="h-10 w-10 text-primary-foreground" strokeWidth={2.5} />
            <h1 className="text-4xl font-bold text-primary-foreground md:text-6xl">
              किसान पुस्तकालय
            </h1>
          </div>
          <p className="mt-4 max-w-2xl text-base font-medium text-primary-foreground/95 drop-shadow md:text-lg">
            खेती-किसानी की बेहतरीन किताबें — पढ़ें और मुफ्त डाउनलोड करें
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-10">
        {/* Search */}
        <div className="mx-auto max-w-2xl">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="किताब या श्रेणी खोजें..."
              className="h-14 rounded-full border-2 pl-12 text-base shadow-sm w-full border-border focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Categories */}
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCat(cat)}
              className={`rounded-full border px-5 py-2 text-sm font-medium transition-all ${
                activeCat === cat
                  ? "border-primary bg-primary text-primary-foreground shadow-md"
                  : "border-border bg-card text-foreground hover:border-primary/40 hover:bg-secondary"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Books grid */}
        <section className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((book) => (
            <div
              key={book.title}
              className="group flex flex-col overflow-hidden rounded-lg border border-border/60 bg-card shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="relative aspect-[4/3] overflow-hidden">
                <img
                  src={book.cover}
                  alt={book.title}
                  loading="lazy"
                  width={768}
                  height={768}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute left-3 top-3 bg-primary text-primary-foreground px-3 py-1 rounded-full text-xs font-semibold">
                  {book.category}
                </div>
              </div>
              <div className="flex flex-1 flex-col p-5">
                <h3 className="text-xl font-bold text-foreground">{book.title}</h3>
                <p className="mt-1 text-sm text-primary">by {book.author}</p>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-muted-foreground">
                  {book.desc}
                </p>
                <p className="mt-4 text-xs font-semibold text-muted-foreground">
                  {book.pages} Pages
                </p>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setSelectedBook(book)}
                    className="inline-flex items-center justify-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-semibold text-sm hover:bg-primary/90 transition-all"
                  >
                    <BookOpen className="h-4 w-4" /> Read
                  </button>
                  <button
                    onClick={() => downloadPDF(book)}
                    className="inline-flex items-center justify-center gap-2 border border-primary text-primary px-4 py-2 rounded-lg font-semibold text-sm hover:bg-primary hover:text-primary-foreground transition-all"
                  >
                    <Download className="h-4 w-4" /> Download
                  </button>
                </div>
              </div>
            </div>
          ))}
        </section>

        {filtered.length === 0 && (
          <p className="mt-12 text-center text-muted-foreground">
            कोई किताब नहीं मिली।
          </p>
        )}
      </main>

      {/* Modal - PDF Preview */}
      {selectedBook && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground p-6 flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold">{selectedBook.title}</h2>
                <p className="text-primary-foreground/80 text-sm mt-1">{selectedBook.category} • {selectedBook.pages} pages</p>
              </div>
              <button
                onClick={() => setSelectedBook(null)}
                className="text-primary-foreground hover:bg-white/20 p-2 rounded-lg transition"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* PDF Viewer */}
            <div className="flex-1 overflow-auto bg-gray-100 p-6">
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                {selectedBook.pdfFile ? (
                  <iframe
                    src={`/pdfs/${encodeURIComponent(selectedBook.pdfFile)}`}
                    className="w-full h-full"
                    style={{ minHeight: '500px' }}
                    title={selectedBook.title}
                  />
                ) : (
                  <div className="p-6 text-center text-gray-500">
                    No PDF available
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="border-t p-4 flex gap-3 justify-end bg-gray-50">
              <button
                onClick={() => setSelectedBook(null)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
              >
                Close
              </button>
              <button 
                onClick={() => downloadPDF(selectedBook)}
                className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2 rounded-lg font-semibold hover:bg-primary/90 transition-all"
              >
                <Download className="h-4 w-4" />
                Download PDF
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default ResourcesPage;
