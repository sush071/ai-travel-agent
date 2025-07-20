import React, { useState, useRef, useEffect, useMemo } from "react";
import "./App.css";

const RenderContent = ({ content }) => {
  if (!content) {
    return null;
  }

  const lines = content.split("\n");
  const elements = [];
  let listItems = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`}>
          {listItems.map((item, index) => (
            <li key={index} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </ul>
      );
      listItems = [];
    }
  };

  const processLineContent = (line) => {
    return line
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Bolding
      .replace(/<b>(.*?)<\/b>/gi, "<strong>$1</strong>") // also handle <b> tags
      .replace(/&lt;b&gt;(.*?)&lt;\/b&gt;/gi, "<strong>$1</strong>") // also handle escaped <b> tags
      .replace(/\*/g, ""); // Remove any other stray asterisks
  };

  lines.forEach((line, i) => {
    const trimmedLine = line.trim();
    if (trimmedLine === "") {
      flushList();
      return;
    }

    if (trimmedLine.startsWith("* ") || trimmedLine.startsWith("- ")) {
      const lineContent = trimmedLine.substring(2).trim();
      listItems.push(processLineContent(lineContent));
    } else {
      // Not a list item, so any current list is finished.
      flushList();
      if (trimmedLine.startsWith("### ")) {
        elements.push(<h4 key={i}>{processLineContent(trimmedLine.substring(4))}</h4>); // Sub-heading
      } else {
        elements.push(<p key={i} dangerouslySetInnerHTML={{ __html: processLineContent(trimmedLine) }} />);
      }
    }
  });

  // Flush any remaining list items at the end
  flushList();

  return elements;
};

const ItineraryAccordion = ({ itinerary }) => {
  const [activeIndex, setActiveIndex] = useState(null);

  // useMemo will prevent re-parsing on every render unless the itinerary changes.
  const parsedItinerary = useMemo(() => {
    if (!itinerary) return [];
    // Split the itinerary by day markers like "**Day 1:**" or "### Day 1:"
    // The lookahead `(?=...)` keeps the delimiter as part of the next string.
    const dayChunks = itinerary.split(/\s*(?=\*\*Day \d+:|### Day \d+:)/).filter(s => s.trim());

    // If parsing fails to find day chunks (e.g., it's just a paragraph),
    // return an empty array to trigger the fallback to RenderContent.
    if (dayChunks.length <= 1 && !itinerary.match(/^\s*(\*\*Day \d+:|### Day \d+:)/)) {
      return [];
    }

    // If the first chunk doesn't start with a day marker, it's likely intro text. Remove it.
    if (dayChunks.length > 0 && !dayChunks[0].match(/^\s*(\*\*Day \d+:|### Day \d+:)/)) {
      dayChunks.shift();
    }

    return dayChunks.map(chunk => {
      const lines = chunk.trim().split('\n');
      const titleLine = lines[0];
      const contentLines = lines.slice(1);
      
      // Clean up title for display
      const title = titleLine.replace(/\*\*|###/g, '').trim();
      const content = contentLines.join('\n');

      return { title, content };
    });
  }, [itinerary]);

  // If parsing did not produce a structured itinerary, fall back to the original renderer.
  if (parsedItinerary.length === 0) {
    return <RenderContent content={itinerary} />;
  }

  const handleToggle = (index) => {
    // If the clicked item is already open, close it. Otherwise, open it.
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <div className="accordion">
      {parsedItinerary.map((day, index) => (
        <div className="accordion-item" key={index}>
          <button className="accordion-title" onClick={() => handleToggle(index)} aria-expanded={activeIndex === index}>
            <span>{day.title}</span>
            <span className="accordion-icon">{activeIndex === index ? '−' : '+'}</span>
          </button>
          {activeIndex === index && (
            <div className="accordion-content">
              {/* Use RenderContent to process the details for the day */}
              <RenderContent content={day.content} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

function App() {
  const [tripData, setTripData] = useState({
    from_city: "",
    destination_city: "",
    start_date: "",
    duration_days: "",
    budget_inr: "",
    interests: "",
  });
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  // 1. Create a ref that will be attached to the results section
  const resultsRef = useRef(null);

  const handleChange = (e) => {
    setTripData({ ...tripData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPlan(null);
    try {
      const res = await fetch("/plan_trip/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...tripData,
          interests: tripData.interests.split(",").map((s) => s.trim()),
        }),
      });
      if (!res.ok) {
        throw new Error("Something went wrong with the request.");
      }
      const data = await res.json();
      setPlan(data.plan);
    } catch (err) {
      console.error(err);
      setPlan("Failed to generate trip plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // 2. Use an effect to scroll to the results when the plan is generated
  useEffect(() => {
    // The effect runs when 'plan' changes. If 'plan' is not null, it means we have results.
    if (plan && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [plan]); // The dependency array ensures this runs only when 'plan' changes.

  return (
    <div className="App">
      <nav className="navbar">
        <h1 className="logo">Lazytrip.xyz</h1>
        <div className="nav-buttons">
          <a href="https://docs.google.com/forms/d/12SvzOvpECGYjpkHgz2lOrFb9VGM6vdzkH3aGHnCULaQ/edit" target="_blank" rel="noopener noreferrer" className="feedback-btn">
            Feedback
          </a>
          <button className="menu-btn">
            <span className="menu-line"></span>
            <span className="menu-line"></span>
            <span className="menu-line"></span>
          </button>
        </div>
      </nav>
      <header
        className="hero-map"
        style={{
          background: `url("/map-background.png") center/cover no-repeat`,
        }}
      >
        <div className="hero-left">
          <form className="hero-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <input id="from_city" name="from_city" value={tripData.from_city} onChange={handleChange} placeholder=" " required />
              <label htmlFor="from_city">From (e.g., Mumbai)</label>
            </div>
            <div className="form-group">
              <input id="destination_city" name="destination_city" value={tripData.destination_city} onChange={handleChange} placeholder=" " required />
              <label htmlFor="destination_city">Destination (e.g., Paris)</label>
            </div>
            <div className="form-group">
              <input id="start_date" name="start_date" type="date" value={tripData.start_date} onChange={handleChange} placeholder=" " required />
              <label htmlFor="start_date">Start Date</label>
            </div>
            <div className="form-group">
              <input id="duration_days" name="duration_days" value={tripData.duration_days} onChange={handleChange} placeholder=" " required />
              <label htmlFor="duration_days">Duration (e.g., 7 days)</label>
            </div>
            <div className="form-group">
              <input id="budget_inr" name="budget_inr" value={tripData.budget_inr} onChange={handleChange} placeholder=" " required />
              <label htmlFor="budget_inr">Budget (e.g., 100,000 INR)</label>
            </div>
            <div className="form-group">
              <input id="interests" name="interests" value={tripData.interests} onChange={handleChange} placeholder=" " required />
              <label htmlFor="interests">Interests (e.g., Art, Food)</label>
            </div>
            <button type="submit">{loading ? "Planning..." : "Plan My Trip"}</button>
          </form>
        </div>
        <div className="hero-right">
          <div className="hero-content">
            <h1>Plan Your Dream Trip</h1>
            <p>Let us craft your perfect adventure</p>
          </div>
          <div className="hero-icons">
            <img src="/airplane.png" alt="airplane" className="icon-airplane" />
            <img src="/colosseum.png" alt="colosseum" className="icon-colosseum" />
            <img src="/beach.png" alt="beach" className="icon-beach" />
          </div>
        </div>
      </header>

      <main>
        <section className="ad-container">Advertisement</section>

        {plan && (
          // 3. Attach the ref to the results section element
          <section className="results" ref={resultsRef}>
            <h2>Results</h2>
            {typeof plan === "string" ? (
              <p className="error-message">{plan}</p>
            ) : (
              <div className="plan-details">
                {(plan.transportation || plan.flights) && (
                  <div className="plan-section">
                    <h3><span role="img" aria-label="transportation">🧳</span> Transportation</h3>
                    <RenderContent content={plan.transportation || plan.flights} />
                  </div>
                )}
                {plan.hotels && (
                  <div className="plan-section">
                    <h3><span role="img" aria-label="hotel">🏨</span> Hotels</h3>
                    <RenderContent content={plan.hotels} />
                  </div>
                )}
                {plan.itinerary && (
                  <div className="plan-section">
                    <h3><span role="img" aria-label="map">🗺️</span> Itinerary</h3>
                    <ItineraryAccordion itinerary={plan.itinerary} />
                  </div>
                )}
                {plan.visa && (
                  <div className="plan-section">
                    <h3><span role="img" aria-label="documents">🛂</span> Docs</h3>
                    <RenderContent content={plan.visa} />
                  </div>
                )}
              </div>              
            )}
          </section>          
        )}

        <section className="ad-container">Advertisement</section>
      </main>

      <footer>🚀 Built with 💙</footer>
    </div>
  );
}

export default App;