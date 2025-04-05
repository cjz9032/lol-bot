if (!device.isScreenOn()) {
    device.wakeUp();
    sleep(1000); // 等待设备完全唤醒
    swipe(290, 1500, 300, 500, 900); // 参数分别为起点X、起点Y、终点X、终点Y、滑动时间 ‌‍

    console.verbose("unlock")
    sleep(4000)
}
//home()
//sleep(3000)
// home()
// className("android.widget.RelativeLayout").desc("知游加速器").findOne().click()

//sleep(5000)

//className("android.view.View").text("我的账户").findOne().click()
//sleep(5000)
//className("android.widget.Button").text("小程序登陆 ").findOne().click()

//className("android.view.View").text("领取时长").findOne().click()


//className("android.widget.TextView").text("当前会员可看广告延续时长，非会员点击领取每日时长获得30分钟").findOne()
// click(813,1121)

function clickButtonPosByText(text) {
    var sc = JSON.parse(JSON.stringify(text)).mInfo.mBoundsInScreen
    var x = (sc.right + sc.left) / 2 + Math.random() * 50;
    var y = (sc.bottom + sc.top) / 2 + Math.random() * 20;
    click(x, y)
}

sleep(3000)
while (true) {
    openAppSetting(getPackageName("微信"));
    sleep(1000)
    click("结束运行")
    sleep(1000)
    click("确定")
    home()
    sleep(1000)
    home()
    sleep(1000)
    className("android.widget.RelativeLayout").desc("知游加速器").findOne().click()


    className("android.view.View").text("领取时长").findOne().click()
    sleep(1000)
    className("android.widget.Button").text("看广告领时长(开放) ").findOne().click()
    sleep(5000)

    let triedWaitTimes = 0;
    while (true) {
        if (className("android.widget.TextView").textEndsWith("已获得奖励").findOne(1000)) {
            console.log("有奖励");
            sleep(2000)
            back()
            break;
        } else if (className("android.widget.TextView").textEndsWith("获得奖励").findOne(1000)) {
            console.log("等待奖励");
            // 系统地点击所有可能的按钮
            var buttonTexts = ["详情", "立即", "玩", "游戏", "查看", "了解", "拒绝"];
            for (let index = 0; index < buttonTexts.length; index++) {
                var text = buttonTexts[index];
                let btn = className("android.widget.TextView").textContains(text).findOne(100);
                if (btn) {
                    clickButtonPosByText(btn);
                    sleep(500); // 短暂延迟确保点击注册
                } else {
                    console.log("没找到 " + text);
                }
            }
            sleep(2000)
            for (let index = 0; index < 10; index++) {
                sleep(600)
                click(500 + Math.random() * 300, 1200 + Math.random() * 500)
            }
            sleep(5000)
            triedWaitTimes += 1
            if (triedWaitTimes > 3) {
                console.log("等待超市 ");
                while (true) {
                    back()
                    sleep(1000)
                    if (className("android.widget.TextView").textEndsWith("已获得奖励").findOne(100)) {
                        back()
                        sleep(3000)
                        break;
                    } else if (className("android.widget.TextView").textEndsWith("获得奖励").findOne(1000)) {
                        sleep(3000)
                    }
                }
                console.log("退出等待超市 ");
                break;
            }
        } else {
            console.log("尝试返回");
            back()
            sleep(2000)
        }
    }


    sleep(3000)

}