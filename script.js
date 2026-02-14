/* ---------------- PARSE AI RESPONSE ---------------- */
function parseAI(text){

    const sections = {};
    const parts = text.split("\n");
    let current = "";

    parts.forEach(line=>{
        line=line.trim();

        if(line.endsWith(":")){
            current=line.replace(":","").replace(" ","_").toUpperCase();
            sections[current]=[];
        }
        else if(current && line!==""){
            sections[current].push(line.replace(/^[-•]\s*/,""));
        }
    });

    return sections;
}


/* ---------------- ELEMENTS ---------------- */
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const previewSection = document.getElementById("previewSection");
const previewImage = document.getElementById("previewImage");
const resultsSection = document.getElementById("results");

const errorToast = document.getElementById("errorToast");
const successToast = document.getElementById("successToast");

uploadArea.onclick = () => fileInput.click();


/* ---------------- DRAG DROP ---------------- */
uploadArea.addEventListener("dragover", e=>{
    e.preventDefault();
    uploadArea.style.background="#ffeaf0";
});

uploadArea.addEventListener("dragleave", ()=>{
    uploadArea.style.background="#fff5f7";
});

uploadArea.addEventListener("drop", e=>{
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
});

fileInput.onchange = ()=> handleFile(fileInput.files[0]);


/* ---------------- HANDLE FILE ---------------- */
function handleFile(file){
    if(!file) return;

    const reader = new FileReader();
    reader.onload = e=>{
        previewImage.src = e.target.result;
        previewSection.style.display="block";
        analyzeImage(file);
    };
    reader.readAsDataURL(file);
}


/* ---------------- CALL FLASK ---------------- */
async function analyzeImage(file){

    const formData = new FormData();
    formData.append("file", file);

    try{
        const res = await fetch("/predict",{method:"POST",body:formData});
        const data = await res.json();

        if(data.success){
            showSuccess("Analysis Complete!");
            showResults(data);
        }else{
            showError(data.error);
        }

    }catch(err){
        showError("Server error");
    }
}


/* ---------------- SHOW RESULTS ---------------- */
function showResults(data){

    resultsSection.style.display="block";

    // Skin tone circle
    document.getElementById("toneCircle").style.background = "#c18b52";

    const parsed = parseAI(data.analysis);


    /* ---------- RECOMMENDATIONS ---------- */
    let rec = document.getElementById("recommendations");

    if(!rec){
        rec=document.createElement("div");
        rec.id="recommendations";
        rec.style.marginTop="25px";
        document.querySelector(".results-container").appendChild(rec);
    }

    rec.innerHTML="<h2>Get Recommendations</h2>";

    for(const key in parsed){
        if(key==="SHOPPING_ITEMS") continue;

        const block=document.createElement("div");
        block.style.marginBottom="18px";

        block.innerHTML=`
            <h3>${key.replace("_"," ")}</h3>
            <ul>${parsed[key].map(i=>`<li>${i}</li>`).join("")}</ul>
        `;

        rec.appendChild(block);
    }


    /* ---------- SHOP & STYLE ---------- */
    let shop=document.getElementById("shopContainer");

    if(!shop){
        shop=document.createElement("div");
        shop.id="shopContainer";
        shop.style.marginTop="30px";
        document.querySelector(".results-container").appendChild(shop);
    }

    shop.innerHTML="<h2>Shop Your Style</h2>";

    const items = parsed["SHOPPING_ITEMS"] || [];

    items.forEach(item=>{
        const card=document.createElement("div");
        card.className="shop-card";
        card.style.margin="10px 0";

        card.innerHTML=`
            <div class="shop-card-inner">
                <h4>${item}</h4>
                <button class="shop-btn">Shop Now</button>
            </div>
        `;

        shop.appendChild(card);
    });
}


/* ---------------- TOASTS ---------------- */
function showError(msg){
    errorToast.innerText = msg;
    errorToast.style.display="block";
    setTimeout(()=>errorToast.style.display="none",3000);
}

function showSuccess(msg){
    successToast.innerText = msg;
    successToast.style.display="block";
    setTimeout(()=>successToast.style.display="none",3000);
}
