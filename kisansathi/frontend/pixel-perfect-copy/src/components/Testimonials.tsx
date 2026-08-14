import img_bRer0FkEydJg1pcxxm3ySCJmUW8_png from "../assets/external/bRer0FkEydJg1pcxxm3ySCJmUW8.png";
import img_YRm5Q76lgWnjRRGRnq9KShh4k3U_png from "../assets/external/YRm5Q76lgWnjRRGRnq9KShh4k3U.png";
import img_Y6T0hQcHxf3Tr71IY2db3Pq1wGo_png from "../assets/external/Y6T0hQcHxf3Tr71IY2db3Pq1wGo.png";
const testimonials = [
  {
    text: "The freshest produce I've ever had! The quality and taste are unmatched. I love knowing exactly where my food comes from. We've been buying our vegetables from this farm for years. The commitment to organic practices really shows in the flavor and health benefits.",
    img: img_bRer0FkEydJg1pcxxm3ySCJmUW8_png,
    name: "Victoria Campbell",
    role: "Customer",
  },
  {
    text: "The difference in taste and quality is clear when you buy from this farm. The produce is not only delicious but also packed with nutrients, thanks to their organic practices. We've been buying our vegetables here for years, and it's been a game-changer for our family's health.",
    img: img_YRm5Q76lgWnjRRGRnq9KShh4k3U_png,
    name: "Ethan Walker",
    role: "Customer",
  },
  {
    text: "The freshest produce I've ever had! The quality and taste are unmatched. I love knowing exactly where my food comes from. We've been buying our vegetables from this farm for years. The commitment to organic practices really shows in the flavor and health benefits.",
    img: img_Y6T0hQcHxf3Tr71IY2db3Pq1wGo_png,
    name: "Aleesha Brown",
    role: "Founder, TechMatter",
  },
];

const Testimonials = () => {
  return (
    <section className="py-20 bg-eco-green-dark">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-14">
          <span className="text-eco-yellow font-semibold text-sm uppercase tracking-widest">Happy Customers</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-primary-foreground mt-3">
            Trusted by 100k+ customers
          </h2>
          <div className="flex items-center justify-center gap-3 mt-6">
            <span className="font-heading text-5xl font-bold text-eco-yellow">4.5</span>
            <div className="text-left">
              <div className="flex text-eco-yellow text-lg">★★★★★</div>
              <span className="text-primary-foreground/60 text-sm">From 400k+ ratings</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div key={i} className="bg-eco-green/30 border border-eco-green-light/20 rounded-2xl p-6">
              <p className="text-primary-foreground/80 text-sm leading-relaxed mb-6">"{t.text}"</p>
              <div className="flex items-center gap-3">
                <img src={t.img} alt={t.name} className="w-12 h-12 rounded-full object-cover" />
                <div>
                  <h4 className="font-heading text-base font-bold text-primary-foreground">{t.name}</h4>
                  <p className="text-primary-foreground/50 text-xs">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
