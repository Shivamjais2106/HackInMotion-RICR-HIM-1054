import img_L5ZOf1bSsxnFo4iTDv3bamiEk_jpeg from "../assets/external/L5ZOf1bSsxnFo4iTDv3bamiEk.jpeg";
import img_TgRCmSQEBuWCS5PT6mj8xdMcHI_jpeg from "../assets/external/TgRCmSQEBuWCS5PT6mj8xdMcHI.jpeg";
import img_hIiFD3wHpCagiQZtgWVWY7EVU_jpeg from "../assets/external/hIiFD3wHpCagiQZtgWVWY7EVU.jpeg";
import img_axJGVH4VS1vHwtToP5Ej5tFge68_jpeg from "../assets/external/axJGVH4VS1vHwtToP5Ej5tFge68.jpeg";
const projects = [
  {
    img: img_L5ZOf1bSsxnFo4iTDv3bamiEk_jpeg,
    title: "Agriculture Farming",
  },
  {
    img: img_TgRCmSQEBuWCS5PT6mj8xdMcHI_jpeg,
    title: "Fertilizers & Pesticides",
  },
  {
    img: img_hIiFD3wHpCagiQZtgWVWY7EVU_jpeg,
    title: "Eco and Agriculture",
  },
  {
    img: img_axJGVH4VS1vHwtToP5Ej5tFge68_jpeg,
    title: "Harvest Innovations",
  },
];

const Projects = () => {
  return (
    <section className="py-20 bg-eco-green-dark">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="text-center mb-4">
          <span className="text-eco-yellow font-semibold text-sm uppercase tracking-widest">Recently Completed</span>
          <h2 className="font-heading text-3xl md:text-5xl font-bold text-primary-foreground mt-3">
            Recently Completed Project
          </h2>
          <p className="text-primary-foreground/60 max-w-2xl mx-auto mt-4 text-sm">
            Affordable rental of well-maintained farming equipment to support your agricultural needs. Innovative irrigation solutions to ensure efficient water use and healthy crops.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
          {projects.map((project, i) => (
            <div key={i} className="group cursor-pointer">
              <div className="relative h-72 rounded-2xl overflow-hidden">
                <img
                  src={project.img}
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-eco-green-dark/70 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4">
                  <h4 className="font-heading text-lg font-bold text-primary-foreground">{project.title}</h4>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-10">
          <a
            href="#"
            className="inline-flex items-center gap-3 bg-eco-yellow text-eco-green-dark font-semibold px-7 py-4 rounded-full text-sm hover:brightness-110 transition-all"
          >
            See All Projects
            <span className="bg-eco-green-dark text-eco-yellow rounded-full w-7 h-7 flex items-center justify-center">→</span>
          </a>
        </div>
      </div>
    </section>
  );
};

export default Projects;
