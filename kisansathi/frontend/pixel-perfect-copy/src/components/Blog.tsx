import img_aek0FPiSf91wz18pKlj3LHmnk_jpg from "../assets/external/aek0FPiSf91wz18pKlj3LHmnk.jpg";
import img_OyY3c2eFixE6QdyK31ITvt06qE_jpg from "../assets/external/OyY3c2eFixE6QdyK31ITvt06qE.jpg";
import img_kDBvPgmJUu0PoQOOoGJ51jkI_jpg from "../assets/external/kDBvPgmJUu0PoQOOoGJ51jkI.jpg";
import img_oQUizHB3hYFo828bpE4kLo3SEQ_jpg from "../assets/external/oQUizHB3hYFo828bpE4kLo3SEQ.jpg";
import img_elT5M1WczMBkBgziVZBqNmorGOU_jpg from "../assets/external/elT5M1WczMBkBgziVZBqNmorGOU.jpg";
const blogs = [
  {
    img: img_aek0FPiSf91wz18pKlj3LHmnk_jpg,
    tag: "Agriculture Life",
    date: "September 14, 2024",
    title: "The Benefits of Eating Local and Seasonal Produce",
  },
  {
    img: img_OyY3c2eFixE6QdyK31ITvt06qE_jpg,
    tag: "Green Farming",
    date: "September 4, 2024",
    title: "How to Start Your Own Small-Scale Organic Garden",
  },
  {
    img: img_kDBvPgmJUu0PoQOOoGJ51jkI_jpg,
    tag: "Sustainable Farming",
    date: "September 23, 2024",
    title: "Sustainable Farming Practices for a Healthier Planet",
  },
  {
    img: img_oQUizHB3hYFo828bpE4kLo3SEQ_jpg,
    tag: "Eco Farming",
    date: "October 12, 2024",
    title: "Why Organic Farming is the Future of Agriculture",
  },
  {
    img: img_elT5M1WczMBkBgziVZBqNmorGOU_jpg,
    tag: "Healthy Soil",
    date: "October 3, 2024",
    title: "The Role of Technology in Modern Sustainable Farming",
  },
];

const Blog = () => {
  return (
    <section id="blog" className="py-20 bg-eco-cream">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-14">
          <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">Agriculture Updates</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3">
            Our Blog & Articles
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {blogs.slice(0, 3).map((blog, i) => (
            <div key={i} className="group cursor-pointer relative h-[400px] rounded-2xl overflow-hidden">
              <img
                src={blog.img}
                alt={blog.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-eco-green-dark/90 via-eco-green-dark/30 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="flex items-center gap-3 mb-3">
                  <span className="bg-eco-yellow text-eco-green-dark text-xs font-semibold px-3 py-1 rounded-full">{blog.tag}</span>
                  <span className="text-primary-foreground/60 text-xs">{blog.date}</span>
                </div>
                <h4 className="font-heading text-xl font-bold text-primary-foreground leading-snug">{blog.title}</h4>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          {blogs.slice(3).map((blog, i) => (
            <div key={i} className="group cursor-pointer relative h-[300px] rounded-2xl overflow-hidden">
              <img
                src={blog.img}
                alt={blog.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-eco-green-dark/90 via-eco-green-dark/30 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <div className="flex items-center gap-3 mb-3">
                  <span className="bg-eco-yellow text-eco-green-dark text-xs font-semibold px-3 py-1 rounded-full">{blog.tag}</span>
                  <span className="text-primary-foreground/60 text-xs">{blog.date}</span>
                </div>
                <h4 className="font-heading text-xl font-bold text-primary-foreground leading-snug">{blog.title}</h4>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Blog;
