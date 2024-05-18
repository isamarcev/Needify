import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano, contractAddress, beginCell } from '@ton/core';
import { JobOffer } from '../wrappers/JobOffer';

import { buildOnchainMetadata } from "../utils/jetton-helpers";
import { TokenWallet } from '../wrappers/TokenWallet';
import { TokenMaster } from "../build/TokenMaster/tact_TokenMaster"
import '@ton/test-utils';
import { log } from 'console';

const jettonParams = {
    name: "Best Practice",
    description: "This is description of Test tact jetton",
    symbol: "XXXE",
    image: "https://play-lh.googleusercontent.com/ahJtMe0vfOlAu1XJVQ6rcaGrQBgtrEZQefHy7SXB7jpijKhu1Kkox90XDuH8RmcBOXNn",
};
let content = buildOnchainMetadata(jettonParams);

let title = "hello"
let description = "world worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld worldworld world" 
let price = toNano(100)
let order = "past simple"


async function DeployContractByContract(JW: SandboxContract<TokenWallet>, by_contract: SandboxContract<JobOffer>) {
    let deploy_am = toNano("1.64")
}
const deployAmount = toNano("0.65")

async function DeployDefaultContract(contract: any, deployer: any, deploy_message: String = "Deploy") {
    let s = await contract.send(
        deployer.getSender(),
        {
            value: deployAmount,
        },
        {
            $$type: deploy_message,
            queryId: 0n
        }
    )
    return s
}

describe('JobOffer', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let platform: SandboxContract<TreasuryContract>;

    let poster: SandboxContract<TreasuryContract>;
    let doer: SandboxContract<TreasuryContract>;

    let jobOffer: SandboxContract<JobOffer>;
    let token: SandboxContract<TokenMaster>;
    let posterJW: SandboxContract<TokenWallet>;
    let deployerJW: SandboxContract<TokenWallet>;
    let doerJettonWallet: SandboxContract<TokenWallet>;
    let jobOfferJettonWallet: SandboxContract<TokenWallet>;
    let userWallet: any;
    const JettonDecimal = 9

    
    beforeEach(async () => {
        blockchain = await Blockchain.create();
        platform = await blockchain.treasury("platform")
        deployer = await blockchain.treasury("deployer");
        poster = await blockchain.treasury("poster");
        doer = await blockchain.treasury("doer")
        token = blockchain.openContract(await TokenMaster.fromInit(deployer.address, content));
        // deploy contract
        let res = await token.send(
                deployer.getSender(),
                {
                    value: deployAmount,
                },
                "Mint: 100"
            )
        // log(await jobOfferJettonWallet.getGetWalletData())

        // log(await jobOffer.getJobData())
        // here is field my_jetton_address: EQDA3JZpNi6juYnNKNrF4GfrW9C_f_WI0gkQuoCy42jLv8dh
        // calculated by Tact contract
        // fun jetton_wallet_address(): Address {
        // let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);
        // let wallet_address: Address = contractAddress(init);
        // return wallet_address;
    // }
        // EQBeoUvcjxLgY99xKaV2VcPiYmEUTNSKT69IfpVgM6KfK2lN
    });

    it('should mint', async () => {
        // let result = await token.send(
        //     deployer.getSender(),
        //     {
        //         value: deployAmount,
        //     },
        //     "Mint: 100"
        // )
        // log(deployerJW.address, "deployer JW address")
        // log(await token.getGetWalletAddress(deployer.address), "Deployer JW from master")
        // log(token.address, "Token Address")
        // await deployerJW.send(
        //     deployer.getSender(),
        //     {
        //         value: toNano(10)
        //     },
        //     {
        //         $$type: "Deploy",
        //         queryId: 1n
        //     }
        // )
        // log(await deployerJW.getGetWalletData())

        // await token.getGetJettonData()
        // let depJWdata = await deployerJW.getGetWalletData()


    });

    // it("Test: Minting is successfully", async () => {
    //     // const TotalSupplyBefore = (await token.getGetJettonData()).total_supply
    //     // deployerJW = await userWallet(deployer.address)
    //     // let initialJettonBalance = toNano('1000.23');
    //     // const mintResult = await token.send(
    //     //     deployer.getSender(),
    //     //     {
    //     //         value: 10000n
    //     //     },
    //     //     "Mint: 100")

    //     // expect(mintResult.transactions).toHaveTransaction({
    //     //     from: token.address,
    //     //     to: deployerJW.address,
    //     //     deploy: true,
    //     // });
    //     // expect(mintResult.transactions).toHaveTransaction({ // excesses
    //     //     from: deployerJW.address,
    //     //     to: token.address
    //     // });
            

    // });

    // it("Test: send transfers", async () => {
    // });

    // it("Test: Deploy offer", async () => {
    // });

    // it("Test: Revoke offer", async () => {
       
    // });
});
