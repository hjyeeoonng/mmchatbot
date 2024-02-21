const canvas = document.getElementById("jsCanvas");
const ctx = canvas.getContext("2d");
const colors = document.getElementsByClassName("jsColor");
const range = document.getElementById("jsRange");
const mode = document.getElementById("jsMode");
const saveBtn = document.getElementById("jsSave");
const change = document.getElementById("jsChange");

const INITIAL_COLOR = "#000000";
const CANVAS_SIZE = 700

ctx.strokeStyle = "#2c2c2c";

canvas.width = CANVAS_SIZE;
canvas.height = CANVAS_SIZE;

ctx.fillStyle = "white";
ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

ctx.strokeStyle = INITIAL_COLOR;
ctx.fillStyle = INITIAL_COLOR;
ctx.lineWidth = 5; /* 라인 굵기 */

let painting = false;
let filling = false;

function stopPainting() {
    painting = false;
}

function startPainting() {
    painting = true;
}

function onMouseMove(event) {
    const x = event.offsetX;
    const y = event.offsetY;
    if (!painting) {
        ctx.beginPath();
        ctx.moveTo(x, y);
    } else{
        ctx.lineTo(x, y);
        ctx.stroke();
    }
}

function handleColorClick(event) {
  const color = event.target.style.backgroundColor;
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
}

function handleRangeChange(event) {
    const size = event.target.value;
    ctx.lineWidth = size;
  }

function handleModeClick() {
 if (filling === true) {
   filling = false;
   mode.innerText = "Fill";
 } else {
  filling = true;
  mode.innerText = "Paint";  
 }
}

function handleCanvasClick() {
    if (filling) {
      ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    }
  }

// 우클릭 방지

function handleCM(event) {
   event.preventDefault();
 }

function changePicture(){
      // const canvas = document.getElementById('myCanvas');

      // 3. 이미지 객체 생성
      const img = new Image();
      // 4. 이미지 소스 설정
      img.src ='./static/js/change.png';
      

      console.log(img.onload)     

      // 5. 이미지 로드이벤트- 콜백함수 등록
      img.onload = function(){
          // 이미지 그리기
          ctx.drawImage(img,0,0,CANVAS_SIZE,CANVAS_SIZE);
      }
}




function handleSaveClick() {
  // const image = canvas.toDataURL("image/png");
  // const link = document.createElement("a");
  // link.href = image;
  // link.download = "PaintJS[EXPORT]";
  // link.click();
 
//여기부터
  
  const imgBase64 = canvas.toDataURL('image/jpeg', 'image/octet-stream');
  const decodImg = atob(imgBase64.split(',')[1]);

  let array = [];
  for (let i = 0; i < decodImg .length; i++) {
    array.push(decodImg .charCodeAt(i));
  }

  const file = new Blob([new Uint8Array(array)], {type: 'image/jpeg'});
  const fileName = 'canvas_img_' + new Date().getMilliseconds() + '.jpg';
  let formData = new FormData();
  formData.append('file', file, fileName);
  
  /* key 확인하기 */
for (let key of formData.keys()) {
  console.log("키값");
  console.log(key);
}

/* value 확인하기 */
for (let value of formData.values()) {
  console.log("벨유값");
   console.log(value);
}


  $.ajax({
    type: 'post',
    url: '/send/image',
    cache: false,
    data: formData,
    processData: false,
    contentType: false,
    success: function (data) {
      alert('Uploaded !!')
    }
  })
  //여기



  
}

if (canvas) {
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mousedown", startPainting);
    canvas.addEventListener("mouseup", stopPainting);
    canvas.addEventListener("mouseleave", stopPainting);
    canvas.addEventListener("click", handleCanvasClick);
    // canvas.addEventListener("contextmenu", handleCM);

}

Array.from(colors).forEach(color => 
    color.addEventListener("click", handleColorClick));

    
if (range) {
    range.addEventListener("input", handleRangeChange);
}
  
if (mode) {
    mode.addEventListener("click", handleModeClick);
}

if (saveBtn){
  saveBtn.addEventListener("click", handleSaveClick);
}

if (change){
  change.addEventListener("click", changePicture);
}