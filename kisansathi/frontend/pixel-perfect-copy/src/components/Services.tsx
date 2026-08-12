import { useRef, useState } from "react";

import img_bqaxUASa5A08yAw5qVEICzHOn4_jpg from "../assets/external/bqaxUASa5A08yAw5qVEICzHOn4.jpg";
import img_DPeZE54kzc2js4Xf73KTcPrc_jpg from "../assets/external/DPeZE54kzc2js4Xf73KTcPrc.jpg";
import img_img_7TTGVQatUt6ZqPwPMgivWqDw0_jpg from "../assets/external/7TTGVQatUt6ZqPwPMgivWqDw0.jpg";
import img_M8tI7NdRSgpiivxj9uyWX5PZI_jpg from "../assets/external/M8tI7NdRSgpiivxj9uyWX5PZI.jpg";
import img_iRKO0IDGnvtY3dHG1DSocvCs_jpg from "../assets/external/iRKO0IDGnvtY3dHG1DSocvCs.jpg";
import img_yCV0RMAsrN9eWEhhsanFn2reQE_jpg from "../assets/external/yCV0RMAsrN9eWEhhsanFn2reQE.jpg";

const services = [
  {
    img: img_bqaxUASa5A08yAw5qVEICzHOn4_jpg,
    tag: "Agricultural Consulting",
    title: "Agricultural Consulting",
    desc: "Commitment to organic chemical free produce from the farm.",
  },
  {
    img: img_DPeZE54kzc2js4Xf73KTcPrc_jpg,
    tag: "Soil Enhancement",
    title: "Soil Fertilization",
    desc: "Comprehensive soil testing and enhancement strategies for growth.",
  },
  {
    img: img_img_7TTGVQatUt6ZqPwPMgivWqDw0_jpg,
    tag: "Animal Husbandry",
    title: "Dairy Production",
    desc: "Direct delivery of fresh, farm grown produce straight to your doorstep.",
  },
  {
    img: img_M8tI7NdRSgpiivxj9uyWX5PZI_jpg,
    tag: "Organic Farming",
    title: "Nutrition Solutions",
    desc: "Committed to growing crops without harmful chemicals for natural produce.",
  },
  {
    img: img_iRKO0IDGnvtY3dHG1DSocvCs_jpg,
    tag: "Seasonal Market",
    title: "Hydroponic System",
    desc: "Eco-friendly farming methods that protect the environment promote .",
  },
  {
    img: img_yCV0RMAsrN9eWEhhsanFn2reQE_jpg,
    tag: "Farm Delivery",
    title: "Product Supplies",
    desc: "Sustainable and efficient farming practices to fresh produce year-round.",
  },
];

const Services = () => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const updateScrollButtons = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 10);
    }
  };

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const amount = 380;
      scrollRef.current.scrollBy({ left: direction === "left" ? -amount : amount, behavior: "smooth" });
      setTimeout(updateScrollButtons, 400);
    }
  };

  return (
    <section id="services" className="py-20 bg-eco-cream">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
      </div>

      {/* Horizontal scroll carousel */}
      <div className="relative">
        <div
          ref={scrollRef}
          onScroll={updateScrollButtons}
          className="flex gap-6 overflow-x-auto scrollbar-hide px-6 lg:px-16 pb-4"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          {services.map((service, i) => (
            <div
              key={i}
              className="group flex-shrink-0 w-[350px] bg-background rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="relative h-56 overflow-hidden">
                <img
                  src={service.img}
                  alt={service.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <span className="absolute top-4 left-4 bg-eco-yellow text-eco-green-dark text-xs font-semibold px-3 py-1.5 rounded-full">
                  {service.tag}
                </span>
              </div>
              <div className="p-6">
                <h4 className="font-heading text-xl font-bold text-foreground mb-2">{service.title}</h4>
                <p className="text-muted-foreground text-sm leading-relaxed">{service.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Navigation arrows */}
        <div className="flex justify-center gap-3 mt-6">
          <button
            onClick={() => scroll("left")}
            disabled={!canScrollLeft}
            className="w-12 h-12 rounded-full border-2 border-eco-green flex items-center justify-center text-eco-green hover:bg-eco-green hover:text-primary-foreground transition-colors disabled:opacity-30"
          >
            ←
          </button>
          <button
            onClick={() => scroll("right")}
            disabled={!canScrollRight}
            className="w-12 h-12 rounded-full bg-eco-green flex items-center justify-center text-primary-foreground hover:bg-eco-green-light transition-colors disabled:opacity-30"
          >
            →
          </button>
        </div>
      </div>
    </section>
  );
};

export default Services;
