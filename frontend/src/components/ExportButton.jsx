import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export default function ExportButton() {
  const handleExport = async () => {
    const element = document.getElementById("report");

    if (!element) {
      alert("Report not found!");
      return;
    }

    // ⏳ wait for DOM to fully render
    await new Promise((resolve) => setTimeout(resolve, 500));

    const canvas = await html2canvas(element, {
      scale: 2, // better quality
      useCORS: true,
      backgroundColor: "#ffffff", // 🔥 MOST IMPORTANT FIX
    });

    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "mm", "a4");

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = (canvas.height * pageWidth) / canvas.width;

    pdf.addImage(imgData, "PNG", 0, 0, pageWidth, pageHeight);
    pdf.save("Legal_Report.pdf");
  };

  return (
    <button
      onClick={handleExport}
      className="bg-purple-500 hover:bg-purple-600 px-4 py-2 rounded"
    >
      📄 Export Report
    </button>
  );
}