import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano, beginCell, contractAddress, Address, address, SendMode, fromNano } from '@ton/core';
import { JobOffer } from '../wrappers/JobOffer';
import { Approve } from '../build/JobOffer/tact_TokenWallet';
import { SenderArguments } from '@ton/core';
import { ContractSystem } from "@tact-lang/emulator";
import { buildOnchainMetadata } from "../utils/jetton-helpers";
import { TokenWallet } from '../wrappers/TokenWallet';
import { Transfer } from '../wrappers/TokenMaster';
import { TokenMaster, Mint } from "../build/TokenMaster/tact_TokenMaster"
import '@ton/test-utils';
import { assert, log } from 'console';
import { JettonWallet, internal, WalletContractV4 } from '@ton/ton';
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

async function DeployOffer(contract: any, poster: any) {
    let deploy_am = toNano("1.64")
    let s = await contract.send(
        poster.getSender(),
        {
            value: deploy_am,
        },
        "Deploy"
    )
    log(s, "DeployOfferFUNC")
    return s
}

describe('JobOffer', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let deployer_contract: SandboxContract<TreasuryContract>;

    let poster: SandboxContract<TreasuryContract>;
    let doer: SandboxContract<TreasuryContract>;

    let jobOffer: SandboxContract<JobOffer>;
    let token: SandboxContract<TokenMaster>;
    let posterJettonWallet: SandboxContract<TokenWallet>;
    let deployerJettonWallet: SandboxContract<TokenWallet>;
    let doerJettonWallet: SandboxContract<TokenWallet>;
    let jobOfferJettonWallet: SandboxContract<TokenWallet>;

    const JettonDecimal = 9

    
    beforeEach(async () => {
        blockchain = await Blockchain.create();
        deployer = await blockchain.treasury("deployer");
        deployer_contract = await blockchain.openContract(deployer)
        poster = await blockchain.treasury("poster");
        doer = await blockchain.treasury("doer")
        // player = await blockchain.treasury("player");
        log(deployer.init)
        log("DEPINIT")
        // log(deployer_address, unb_deployer_address, "DEPADDRESSES")
        token = blockchain.openContract(await TokenMaster.fromInit(deployer.address, content));
        jobOffer = blockchain.openContract(await JobOffer.fromInit(
            title, description, price, order, token.address
        ))
        let JOWallet = blockchain.openContract(await TokenWallet.fromInit(
            jobOffer.address, token.address
        ))
        let ress = await JOWallet.send(
            poster.getSender(),
            {
                value: toNano(0.64)
            },
            {
                $$type: "Deploy",
                queryId: 0n
            }
        )
        // Send Transaction
        const deployResult = await token.send(deployer.getSender(), { value: toNano("10") }, "Mint: 100");
        expect(deployResult.transactions).toHaveTransaction({
            from: deployer.address,
            to: token.address,
            deploy: true,
            success: true,
        });

        const deployerWallet = await token.getGetWalletAddress(deployer.address);
        deployerJettonWallet = blockchain.openContract(TokenWallet.fromAddress(deployerWallet));

        const posterWallet = await token.getGetWalletAddress(poster.address)
        posterJettonWallet = blockchain.openContract(TokenWallet.fromAddress(posterWallet));

        const doerWalletAddress = await token.getGetWalletAddress(doer.address)
        doerJettonWallet = blockchain.openContract(TokenWallet.fromAddress(doerWalletAddress));

        const jobOfferWalletAddress = await token.getGetWalletAddress(jobOffer.address)
        jobOfferJettonWallet = blockchain.openContract(await TokenWallet.fromAddress(jobOffer.address));

        // let sender: SenderArguments = {
        //     value: toNano(2),
        //     to: jobOfferJettonWallet.address,
        //     sendMode: SendMode.IGNORE_ERRORS,
        //     bounce: false,

        // }
        // await jobOffer.send(
        //     sender,
        //     {
        //         value: toNano(0.3),

        //     }
        // )
    });

    it("Test: Minting is successfully", async () => {
        const totalSupplyBefore = (await token.getGetJettonData()).total_supply;
        const mintAmount = toNano(100);
        const Mint: Mint = {
            $$type: "Mint",
            amount: mintAmount,
            receiver: deployer.address,
        };
        const mintResult = await token.send(deployer.getSender(), { value: toNano("10") }, Mint);
        expect(mintResult.transactions).toHaveTransaction({
            from: deployer.address,
            to: token.address,
            success: true,
        });
        // printTransactionFees(mintResult.transactions);

        const totalSupplyAfter = (await token.getGetJettonData()).total_supply;
        expect(totalSupplyBefore + mintAmount).toEqual(totalSupplyAfter);

        const walletData = await deployerJettonWallet.getGetWalletData();
        expect(walletData.owner).toEqualAddress(deployer.address);
        expect(walletData.balance).toBeGreaterThanOrEqual(mintAmount);

        const transferAmount = toNano(80);
        // Here is a problem TypeError: Do not know how to serialize a BigInt
        const transferMessage: Transfer = {
            $$type: "Transfer",
            query_id: 0n,
            amount: transferAmount,
            destination: poster.address,
            response_destination: deployer.address,
            custom_payload: null,
            forward_ton_amount: toNano("0.1"),
            forward_payload: beginCell().endCell(),
        };

        const transfer_res = await token.send(deployer.getSender(), { value: toNano("10") }, transferMessage);
        const second = await deployerJettonWallet.getGetWalletData();
        log(second.balance)
    });

    it("Test: send transfers", async () => {
        let transferAmount = toNano(80);
        // Here is a problem TypeError: Do not know how to serialize a BigInt
        const transferMessage: Transfer = {
            $$type: "Transfer",
            query_id: 0n,
            amount: transferAmount,
            destination: poster.address,
            response_destination: deployer.address,
            custom_payload: null,
            forward_ton_amount: toNano("0.1"),
            forward_payload: beginCell().endCell(),
        };
        transferAmount = toNano(20)
        await token.send(deployer.getSender(), { value: toNano("10") }, transferMessage);
        const secondTransferMessage: Transfer = {
            $$type: "Transfer",
            query_id: 1n,
            amount: transferAmount,
            destination: deployer.address,
            response_destination: poster.address,
            custom_payload: null,
            forward_ton_amount: toNano("0.1"),
            forward_payload: beginCell().endCell(),
        };
        await posterJettonWallet.send(poster.getSender(), { value: toNano("10") }, secondTransferMessage);
        const poster_data1 = await posterJettonWallet.getGetWalletData();
        await posterJettonWallet.send(poster.getSender(), { value: toNano("10") }, secondTransferMessage);
        const poster_data2 = await posterJettonWallet.getGetWalletData();
        await token.send(deployer.getSender(), { value: toNano("10") }, transferMessage);
        const ThirdTransferMessage: Transfer = {
            $$type: "Transfer",
            query_id: 1n,
            amount: transferAmount,
            destination: doer.address,
            response_destination: poster.address,
            custom_payload: null,
            forward_ton_amount: toNano("0.1"),
            forward_payload: beginCell().endCell(),
        };
        await posterJettonWallet.send(poster.getSender(), { value: toNano("10") }, ThirdTransferMessage);
        const deployer_data = await deployerJettonWallet.getGetWalletData();
        const poster_data = await posterJettonWallet.getGetWalletData();
        const doer_data = await doerJettonWallet.getGetWalletData();
    });

    it("Test: Deploy offer", async () => {
        let res = await DeployOffer(jobOffer, poster)
    });

    it("Test: Revoke offer", async () => {
        // Mint tokens to poster JettonWallet
        let mintAmount = BigInt(120 * 10 ** JettonDecimal);
        const Mint: Mint = {
            $$type: "Mint",
            amount: mintAmount,
            receiver: poster.address,
        };
        const mintResult = await token.send(deployer.getSender(), { value: toNano("0.5") }, Mint);
        let PosterJWData = await posterJettonWallet.getGetWalletData()
        log(fromNano(PosterJWData.balance), "Poster Jetton Data after mint")
        expect(mintAmount).toEqual(PosterJWData.balance)
        let DODeploy = await DeployOffer(jobOffer, poster)
        let transferAmount = price
        // Send to offer_jetton_wallet
        let TransferMessage: Transfer = {
            $$type: "Transfer",
            query_id: 1n,   
            amount: transferAmount,
            destination: jobOffer.address,
            response_destination: poster.address,
            custom_payload: null,
            forward_ton_amount: toNano("0.64"),
            forward_payload: beginCell().endCell(),
        };

        await posterJettonWallet.send(poster.getSender(), { value: toNano("10") }, TransferMessage);
        PosterJWData = await posterJettonWallet.getGetWalletData()
        log(fromNano(PosterJWData.balance), "Poster balance after transfer")
        log(posterJettonWallet.address, "PJW ADDRESS")
        
        // let OfferContractData = await jobOfferJettonWallet.getGetWalletData()
        // assert(OfferContractData.balance == transferAmount)
        
        // // Approve by deployer
        // let ApproveMessage: Approve = {
        //     $$type: "Approve",
        //     amount: transferAmount
        // }
        // let first_send = await jobOffer.send(
        //     deployer.getSender(),
        //     {
        //         value: toNano(0.65)
        //     },
        //     ApproveMessage
        // )
        // // log(jobOffer.address)
        // // return
        // let JOData = await jobOffer.getJobData()
        // assert(JOData.state == 1n)
        
        // // revoke
        // let res = await jobOffer.send(
        //     poster.getSender(),
        //     {
        //         value: toNano(0.64)
        //     },
        //     "revoke"
        // )

        // // log(res.events)
        // JOData = await jobOffer.getJobData()
        // assert(JOData.state == 6n)
        
        // PosterJWData = await posterJettonWallet.getGetWalletData()
        // log(fromNano(PosterJWData.balance), "Poster balance after revoke")
        // let OfferJWD = await jobOfferJettonWallet.getGetWalletData()
        // log(OfferJWD.balance, "Offer JW balance after")
        
        
        // log(fromNano(JOData.balance), "JO Balance")
        // log(JOData, "JO Data")
        // log(poster.address, "Poster address")
        // log(jobOfferJettonWallet.address)
        // log(JOData.owner)
        // assert(JOData.owner == poster.address)
        // await jobOfferJettonWallet.send(
        //     Address.parseRaw(jobOffer.address).getSender(),
        //     {
        //         value: 20n,
        //     },
        //     TransferMessage
        // )


        // await deployer.send(
        //     to: deployer.getSender(),
        //     value: toNano(0.05),
        //     body: ApproveMessage,
        // )

        // let deploy_am = toNano("0.15")
        // await jobOffer.send(
        //     deployer.getSender(),
        //     {
        //         value: deploy_am,
        //     },
        //     "revoke"
        // )
        // let res = await jobOffer.getJobData()
        // log(res)
    });
    
        // const baker1 = await blockchain.treasury('baker1')
        // const baker2 = await blockchain.treasury('baker2')

        // const totalSupplyBefore = (await jetton_master_contract.getGetJettonData()).total_supply
        // log(totalSupplyBefore)
        // const mintAmount = toNano(10);
        // const Mints: Mint = {
        //     $$type: "Mint",
        //     amount: mintAmount,
        //     receiver: poster.address,
        // };
        // const mintResult = await jetton_master_contract.send(
        //     deployer.getSender(), { value: toNano("10"), bounce: false }, Mints);
        // const s = await jetton_master_contract.send(
        //     deployer.getSender(), { value: toNano("10") }, Mints);

        // const totalSupplyAfter = (await jetton_master_contract.getGetJettonData()).total_supply;
        // log(totalSupplyAfter)

        // const poster_wallet_contract = await jetton_master_contract.getGetWalletAddress(
        //     poster.address
        // )
        // // const senderWallet = deployerJettonWallet;
        // const transferAmount = toNano(80);
        // // Here is a problem TypeError: Do not know how to serialize a BigInt
        // const transferMessage: Transfer = {
        //     $$type: "Transfer",
        //     query_id: 0n,
        //     amount: 10n,
        //     destination: poster.address,
        //     response_destination: deployer.address,
        //     custom_payload: null,
        //     forward_ton_amount: toNano("0.1"),
        //     forward_payload: beginCell().endCell(),
        // };
        // const transferResult = await jetton_master_contract.send(deployer.getSender(), { value: toNano("0.5") }, transferMessage)
        // // log(transferResult)
        // let dep_add = await jetton_master_contract.getGetWalletAddress(deployer.address)
        // let pos_add = await jetton_master_contract.getGetWalletAddress(poster.address)
        // log(dep_add, pos_add)
        // let bal = await deployerJettonWallet.getGetWalletData()
        // let bal2 = await posterJettonWallet.getGetWalletData()

        // log(bal.balance, bal2.balance)
        // let poster_contract = await jetton_master_contract.getGetWalletAddress(poster.address)
        // log(poster_contract)
        // let poster_wal = blockchain.openContract(await TokenWallet.fromInit(poster.address, jetton_master_contract.address))
        // log(await poster_wal.getGetWalletData())


        // let poster_wallet = 

        // const posterBalance = await posterJettonWallet.getGetWalletData()

        // const receiverWalletAddress = await jetton_master_contract.getGetWalletAddress(poster.address);
        // const receiverWallet = blockchain.openContract(TokenWallet.fromAddress(receiverWalletAddress));
        
        // const balancePoster = await posterJettonWallet.getGetWalletData()
        // const balanceSender = await deployerJettonWallet.getGetWalletData()
        
        // log(balanceSender.balance)

        // log(balancePoster.balance)

        // log(balancePoster.master)
        // log(jetton_master_contract.address)


        // expect(walletData.owner).toEqualAddress(deployer.address);
        // expect(walletData.balance).toBeGreaterThanOrEqual(mintAmount);
;
});
