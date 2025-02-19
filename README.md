# timeSliderScaleTool

説明
-

タイムスライダーのレンジをスケールする為のツールです。  
対応mayaVer: 2022  

2025/02/18  リリース

インストール方法
-

1,timeSliderScaleBtn.py　を mayaのpythonPathが通ってるフォルダに格納してください。  
例  C:/Users/Qboz/Documents/maya/2022/scripts/  
  
2,mayaを起動して、下記のスクリプトをpythonで実行してください。  
  
##--------------------------------------  
import timeSliderScaleBtn  
timeSliderScaleBtn.main()  
##--------------------------------------  


使用方法
-

![image](https://github.com/user-attachments/assets/9f53be71-b731-4e43-8b7c-1dd3638649e5)

< scroll scale >  ボタン上でマウスホイールを回転させると、タイムスライダーのレンジが現在のフレームを中心にスケールされます。  
< scroll scale >　ボタンを押下すると、タイムレンジを最大化・スケール後のレンジ　を切り替えます。  

右側ボタン ボタンを押下すると、ボタンの数字分の長さになるように　現在のフレームを中心してきタイムレンジをスケールします。  
右側ボタン　ボタンを右クリックすると、フレームの長さを変更するダイアログがでます。  
