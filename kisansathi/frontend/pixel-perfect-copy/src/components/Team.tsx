import img_Cnjy5md2eJXTEdve7mQq88JQaLE_jpg from "../assets/external/Cnjy5md2eJXTEdve7mQq88JQaLE.jpg";
import img_Wmbqi8Hc2aONJMmo74xZRItlfKI_jpeg from "../assets/external/Wmbqi8Hc2aONJMmo74xZRItlfKI.jpeg";
import img_WxlPsc1aIk6ZgXY3winXdoC35Y_jpg from "../assets/external/WxlPsc1aIk6ZgXY3winXdoC35Y.jpg";
import img_DSvojpqqI1enzvEEn01uKEU5aA_jpeg from "../assets/external/DSvojpqqI1enzvEEn01uKEU5aA.jpeg";
const members = [
  {
    img: img_Cnjy5md2eJXTEdve7mQq88JQaLE_jpg,
    name: "James Albert",
    role: "Lead Farmer",
  },
  {
    img: img_Wmbqi8Hc2aONJMmo74xZRItlfKI_jpeg,
    name: "David M Hower",
    role: "Head of Agricultural Innovation",
  },
  {
    img: img_WxlPsc1aIk6ZgXY3winXdoC35Y_jpg,
    name: "Dennis Poroma",
    role: "Food Farmer",
  },
  {
    img: img_DSvojpqqI1enzvEEn01uKEU5aA_jpeg,
    name: "Floyd Miles",
    role: "Garden Farmer",
  },
];

const Team = () => {
  return (
    <section className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-14">
          <span className="text-eco-green font-semibold text-sm uppercase tracking-widest">Our Farmers</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-foreground mt-3">
            We Have Lot's Of Experience <br /> Team Members
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {members.map((member, i) => (
            <div key={i} className="group cursor-pointer">
              <div className="relative h-80 rounded-2xl overflow-hidden mb-4">
                <img
                  src={member.img}
                  alt={member.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <h4 className="font-heading text-xl font-bold text-foreground">{member.name}</h4>
              <p className="text-muted-foreground text-sm">{member.role}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Team;
